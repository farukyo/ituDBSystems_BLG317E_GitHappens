# Main Routes Module
# Handles homepage, about page, quiz, recommendations, and suggestion form.

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from groq import Groq 
import os
import json
from dotenv import load_dotenv
from sqlalchemy import text
from database.db import engine

load_dotenv()

main_bp = Blueprint('main', __name__)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

@main_bp.route("/search")
def search():
    """Unified search endpoint for movies, series, and episodes"""
    search_query = request.args.get('q', '').strip()
    
    if not search_query:
        flash("Please enter a search term", "warning")
        return redirect(url_for('main.index'))
    
    movies = []
    series = []
    episodes = []
    people = []
    
    with engine.connect() as conn:
        # Search in Movies
        try:
            sql_movies = """
                SELECT movieId, movieTitle, startYear, runtimeMinutes 
                FROM movies 
                WHERE movieTitle LIKE :q 
                LIMIT 20
            """
            movies = conn.execute(text(sql_movies), {"q": f"%{search_query}%"}).fetchall()
        except:
            movies = []
        
        # Search in Series
        try:
            sql_series = """
                SELECT seriesId, seriesTitle, startYear, runtimeMinutes 
                FROM series 
                WHERE seriesTitle LIKE :q 
                LIMIT 20
            """
            series = conn.execute(text(sql_series), {"q": f"%{search_query}%"}).fetchall()
        except:
            series = []
        
        # Search in Episodes
        try:
            sql_episodes = """
                SELECT e.episodeId, e.epTitle, e.runtimeMinutes, e.seNumber, e.epNumber, s.seriesTitle
                FROM Episode e
                JOIN Series s ON e.seriesId = s.seriesId
                WHERE e.epTitle LIKE :q 
                LIMIT 20
            """
            episodes = conn.execute(text(sql_episodes), {"q": f"%{search_query}%"}).fetchall()
        except:
            episodes = []
        
        # Search in People
        try:
            sql_people = """
                SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear
                FROM people p
                WHERE p.primaryName LIKE :q 
                LIMIT 20
            """
            people = conn.execute(text(sql_people), {"q": f"%{search_query}%"}).fetchall()
        except:
            people = []
    
    return render_template("search_results.html", 
                           query=search_query,
                           movies=movies,
                           series=series,
                           episodes=episodes,
                           people=people)

@main_bp.route("/")
def index():
    featured_movies = []
    featured_series = []
    featured_people = []

    with engine.connect() as conn:
        # Top 5 Movies
        try:
            sql_movies = """
                SELECT m.movieId, m.movieTitle, m.startYear, r.averageRating, r.numVotes
                FROM movies m
                JOIN ratings r ON m.movieId = r.titleId
                WHERE r.numVotes > 100000
                ORDER BY r.averageRating DESC
                LIMIT 5
            """
            featured_movies = conn.execute(text(sql_movies)).fetchall()
        except Exception as e:
            print(f"Error fetching featured movies: {e}")

        # Top 5 Series
        try:
            sql_series = """
                SELECT s.seriesId, s.seriesTitle, s.startYear, r.averageRating, r.numVotes
                FROM series s
                JOIN ratings r ON s.seriesId = r.titleId
                WHERE r.numVotes > 100000
                ORDER BY r.averageRating DESC
                LIMIT 5
            """
            featured_series = conn.execute(text(sql_series)).fetchall()
        except Exception as e:
            print(f"Error fetching featured series: {e}")

        # Top 5 People (Most liked actors) - GÜNCELLENDİ
        try:
            sql_people = """
                SELECT
                    p.peopleId,
                    p.primaryName,
                    l.numLikes
                FROM (
                    SELECT people_id, COUNT(*) as numLikes
                    FROM githappens_users.user_likes_people
                    GROUP BY people_id
                ) l
                JOIN people p ON l.people_id = p.peopleId
                LEFT JOIN profession_assignments pa ON p.peopleId = pa.peopleId
                LEFT JOIN profession_dictionary pd ON pa.profession_dict_id = pd.id
                WHERE (pd.name LIKE '%actor%' OR pd.name LIKE '%actress%')
                GROUP BY p.peopleId, p.primaryName, l.numLikes
                ORDER BY l.numLikes DESC
                LIMIT 5
            """
            featured_people = conn.execute(text(sql_people)).fetchall()
        except Exception as e:
            print(f"Error fetching featured people: {e}")

    return render_template("home.html", 
                           featured_movies=featured_movies, 
                           featured_series=featured_series, 
                           featured_people=featured_people)


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/quiz/setup")
@login_required
def quiz_setup():
    top_users = []
    user_rank = 0
    with engine.connect() as conn:
        # Top 5 users
        sql_top = """
            SELECT username, score, gender 
            FROM githappens_users.users 
            ORDER BY score DESC 
            LIMIT 5
        """
        top_users = conn.execute(text(sql_top)).fetchall()
        
        # Current user rank
        sql_rank = """
            SELECT COUNT(*) + 1 
            FROM githappens_users.users 
            WHERE score > (SELECT score FROM githappens_users.users WHERE id = :uid)
        """
        user_rank = conn.execute(text(sql_rank), {"uid": current_user.id}).scalar()

    return render_template("quiz_setup.html", top_users=top_users, user_rank=user_rank)

# Quiz Üretme
@main_bp.route("/quiz/generate", methods=["POST"])
@login_required
def generate_quiz():
    title = request.form.get("title")
    difficulty = request.form.get("difficulty")
    count = int(request.form.get("question_count", 10))

    prompt = f"""
    Create a detailed and fun trivia quiz with {count} multiple-choice questions about the movie/topic: "{title}".
    Difficulty level: {difficulty}.
    Language: English.

    Guidelines:
    1. Focus on specific details, plot points, characters, and iconic scenes if "{title}" is a movie or book.
    2. Ensure the questions are not generic advice but specific to the facts about "{title}".
    3. The tone should be engaging.
    4. Each question must have exactly 4 options.
    5. Avoid mixing languages; use only English.

    You must respond ONLY with a valid JSON object in this format:
    {{
        "questions": [
            {{
                "question": "Soru metni buraya",
                "options": ["Seçenek 1", "Seçenek 2", "Seçenek 3", "Seçenek 4"],
                "answer": "Doğru olan seçeneğin aynısı"
            }}
        ]
    }}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )

        raw_response = chat_completion.choices[0].message.content
        quiz_data = json.loads(raw_response)
        
        # Store difficulty in the quiz data
        quiz_data["difficulty"] = difficulty

        session["quiz"] = quiz_data
        session.modified = True

        return redirect(url_for("main.quiz_play"))

    except Exception as e:
        print("GROQ AI HATASI:", e)
        flash("Quiz oluşturulurken bir hata oluştu.")
        return redirect(url_for("main.quiz_setup"))


# Quiz Oynama Sayfası
@main_bp.route("/quiz/play")
@login_required
def quiz_play():
    quiz = session.get("quiz")
    if not quiz:
        return redirect(url_for("main.quiz_setup"))

    return render_template("quiz_play.html", quiz=quiz)

# Sonuç Hesaplama ve PUAN KAYDETME
@main_bp.route("/quiz/submit", methods=["POST"])
@login_required
def submit_quiz():
    quiz = session.get("quiz")
    
    if not quiz or "questions" not in quiz:
        return redirect(url_for("main.quiz_setup"))

    correct = 0
    questions = quiz["questions"]
    total = len(questions)

    for i, q in enumerate(questions):
        user_answer = request.form.get(f"q{i}")
        if user_answer == q["answer"]:
            correct += 1
            
    # Calculate points based on difficulty
    difficulty = quiz.get("difficulty", "medium")
    multiplier = 1
    if difficulty == "medium":
        multiplier = 2
    elif difficulty == "hard":
        multiplier = 3
    
    total_points = correct * multiplier

    # --- YENİ EKLENEN KISIM: SKORU DATABASE'E YAZ ---
    old_score = 0
    new_score = 0
    percentile = 100
    try:
        with engine.connect() as conn:
            # Get current score before update
            res = conn.execute(text("SELECT score FROM githappens_users.users WHERE id = :uid"), {"uid": current_user.id}).fetchone()
            if res:
                old_score = res[0]
            
            # Update score
            update_sql = "UPDATE githappens_users.users SET score = score + :points WHERE id = :uid"
            conn.execute(text(update_sql), {"points": total_points, "uid": current_user.id})
            conn.commit()
            new_score = old_score + total_points

            # Calculate Percentile (Top X%)
            total_users = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users")).scalar()
            higher_scores = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users WHERE score > :s"), {"s": new_score}).scalar()
            if total_users > 0:
                percentile = (higher_scores / total_users) * 100
    except Exception as e:
        print(f"Skor kaydedilemedi: {e}")
    # -----------------------------------------------

    return render_template(
        "quiz_result.html",
        score=correct,
        total=total,
        points=total_points,
        difficulty=difficulty,
        old_total_score=old_score,
        new_total_score=new_score,
        percentile=round(percentile, 1)
    )


@main_bp.route("/recommend")
@login_required
def recommend():
    user_id = current_user.id
    recommended_movies = []
    recommended_series = []
    top_genres = []
    all_genres = []

    selected_genre = request.args.get('genre')
    start_year = request.args.get('start_year')
    end_year = request.args.get('end_year')

    with engine.connect() as conn:
        all_genres = conn.execute(text("SELECT genreName FROM genres ORDER BY genreName")).fetchall()
        all_genres = [g[0] for g in all_genres]

        target_genre_ids = []
        
        if selected_genre:
            genre_res = conn.execute(text("SELECT genreId FROM genres WHERE genreName = :name"), {"name": selected_genre}).fetchone()
            if genre_res:
                target_genre_ids = [genre_res[0]]
                top_genres = [selected_genre]
        else:
            sql_genres = """
                SELECT g.genreId, g.genreName, COUNT(*) as genre_count
                FROM (
                    SELECT mg.genreId
                    FROM githappens_users.user_likes_titles ul
                    JOIN Movie_Genres mg ON ul.title_id = mg.movieId
                    WHERE ul.user_id = :uid
                    
                    UNION ALL
                    
                    SELECT sg.genreId
                    FROM githappens_users.user_likes_titles ul
                    JOIN Series_Genres sg ON ul.title_id = sg.seriesId
                    WHERE ul.user_id = :uid
                ) as user_genres
                JOIN genres g ON user_genres.genreId = g.genreId
                GROUP BY g.genreId, g.genreName
                ORDER BY genre_count DESC
                LIMIT 3
            """
            top_genres_result = conn.execute(text(sql_genres), {"uid": user_id}).fetchall()
            top_genres = [row.genreName for row in top_genres_result]
            target_genre_ids = [row.genreId for row in top_genres_result]

        year_condition = ""
        params = {"uid": user_id}
        
        if start_year and start_year.isdigit():
            year_condition += " AND m.startYear >= :start_year"
            params["start_year"] = int(start_year)
        if end_year and end_year.isdigit():
            year_condition += " AND m.startYear <= :end_year"
            params["end_year"] = int(end_year)

        series_year_condition = year_condition.replace("m.startYear", "s.startYear")


        if target_genre_ids:
            ids_str = ','.join(map(str, target_genre_ids))
            
            sql_rec_movies = f"""
                SELECT DISTINCT m.movieId, m.movieTitle, m.startYear, r.averageRating, r.numVotes
                FROM movies m
                JOIN Movie_Genres mg ON m.movieId = mg.movieId
                JOIN ratings r ON m.movieId = r.titleId
                WHERE mg.genreId IN ({ids_str})
                AND m.movieId NOT IN (
                    SELECT title_id FROM githappens_users.user_likes_titles WHERE user_id = :uid
                )
                AND r.numVotes > 1000
                {year_condition}
                ORDER BY r.averageRating DESC
                LIMIT 12
            """
            try:
                recommended_movies = conn.execute(text(sql_rec_movies), params).fetchall()
            except Exception as e:
                print(f"Error recommending movies: {e}")

            sql_rec_series = f"""
                SELECT DISTINCT s.seriesId, s.seriesTitle, s.startYear, r.averageRating, r.numVotes
                FROM series s
                JOIN Series_Genres sg ON s.seriesId = sg.seriesId
                JOIN ratings r ON s.seriesId = r.titleId
                WHERE sg.genreId IN ({ids_str})
                AND s.seriesId NOT IN (
                    SELECT title_id FROM githappens_users.user_likes_titles WHERE user_id = :uid
                )
                AND r.numVotes > 1000
                {series_year_condition}
                ORDER BY r.averageRating DESC
                LIMIT 12
            """
            try:
                recommended_series = conn.execute(text(sql_rec_series), params).fetchall()
            except Exception as e:
                print(f"Error recommending series: {e}")

        else:
            sql_top_movies = f"""
                SELECT m.movieId, m.movieTitle, m.startYear, r.averageRating, r.numVotes
                FROM movies m
                JOIN ratings r ON m.movieId = r.titleId
                WHERE r.numVotes > 10000
                {year_condition}
                ORDER BY r.averageRating DESC
                LIMIT 12
            """
            recommended_movies = conn.execute(text(sql_top_movies), params).fetchall()
            
            sql_top_series = f"""
                SELECT s.seriesId, s.seriesTitle, s.startYear, r.averageRating, r.numVotes
                FROM series s
                JOIN ratings r ON s.seriesId = r.titleId
                WHERE r.numVotes > 10000
                {series_year_condition}
                ORDER BY r.averageRating DESC
                LIMIT 12
            """
            recommended_series = conn.execute(text(sql_top_series), params).fetchall()

    return render_template("recommend.html", 
                           movies=recommended_movies, 
                           series=recommended_series,
                           genres=top_genres,
                           all_genres=all_genres,
                           selected_genre=selected_genre,
                           start_year=start_year,
                           end_year=end_year)

@main_bp.route("/api/random_recommendation")
def random_recommendation():
    import random
    is_movie = random.choice([True, False])
    
    with engine.connect() as conn:
        if is_movie:
            sql = """
                SELECT m.movieId as id, m.movieTitle as title, 'movie' as type
                FROM movies m
                JOIN ratings r ON m.movieId = r.titleId
                WHERE r.averageRating > 7.0 AND r.numVotes > 5000
                ORDER BY RAND()
                LIMIT 1
            """
        else:
            sql = """
                SELECT s.seriesId as id, s.seriesTitle as title, 'serie' as type
                FROM series s
                JOIN ratings r ON s.seriesId = r.titleId
                WHERE r.averageRating > 7.0 AND r.numVotes > 5000
                ORDER BY RAND()
                LIMIT 1
            """
        
        result = conn.execute(text(sql)).fetchone()
        
        if result:
            return {
                "id": result.id,
                "title": result.title,
                "type": result.type,
                "url": url_for('movie.movie', movie_id=result.id) if result.type == 'movie' else url_for('series.serie_detail', series_id=result.id)
            }
        else:
            return {"error": "No recommendation found"}, 404


@main_bp.route("/suggest", methods=["GET", "POST"])
@login_required
def suggest():
    if request.method == "POST":
        subject = request.form.get("subject")
        message_body = request.form.get("message")
        
        user_email = current_user.email
        user_name = current_user.username
        
        flash("Thank you! Your suggestion has been sent successfully.")
        return redirect(url_for('main.index'))
        
    return render_template("suggestion.html")