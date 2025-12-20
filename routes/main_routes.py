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
    
    return render_template("search_results.html", 
                           query=search_query,
                           movies=movies,
                           series=series,
                           episodes=episodes)

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

        # Top 5 People (Most liked actors)
        try:
            sql_people = """
                SELECT
                    p.peopleId,
                    p.primaryName,
                    l.numLikes
                FROM (
                    SELECT entity_id, COUNT(*) as numLikes
                    FROM githappens_users.user_likes
                    WHERE entity_type = 'person'
                    GROUP BY entity_id
                ) l
                JOIN people p ON l.entity_id = p.peopleId
                LEFT JOIN profession prof ON p.professionId = prof.professionId
                WHERE (prof.professionName LIKE '%actor%' OR prof.professionName LIKE '%actress%')
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
    return render_template("quiz_setup.html")

# Quiz Üretme: Formdan gelen verileri alır ve session'a kaydeder
@main_bp.route("/quiz/generate", methods=["POST"])
@login_required
def generate_quiz():
    title = request.form.get("title")
    difficulty = request.form.get("difficulty")
    count = int(request.form.get("question_count", 10)) # Sayıyı aldık

    # Yapay zekaya JSON formatında cevap vermesini emrediyoruz
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
        # Groq API Çağrısı
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # Ücretsiz ve çok güçlü bir model
            response_format={"type": "json_object"} # JSON dönmesini garanti eder
        )

        # Yanıtı JSON olarak işle
        raw_response = chat_completion.choices[0].message.content
        quiz_data = json.loads(raw_response)

        # Session'a kaydet
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

# Sonuç Hesaplama
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

    return render_template(
        "quiz_result.html",
        score=correct,  # Artık 'score' 30 değil, 3 olacak
        total=total
    )


@main_bp.route("/recommend")
@login_required
def recommend():
    return render_template("recommend.html")


@main_bp.route("/suggest", methods=["GET", "POST"])
@login_required
def suggest():
    if request.method == "POST":
        subject = request.form.get("subject")
        message_body = request.form.get("message")
        
        # Sender info
        user_email = current_user.email
        user_name = current_user.username
        
        # -------------------------------------------------------
        # MAIL SENDING LOGIC WILL BE ADDED HERE
        # (SMTP or API code to be added in the future)
        # -------------------------------------------------------
        
        flash("Thank you! Your suggestion has been sent successfully.")
        return redirect(url_for('main.index'))
        
    return render_template("suggestion.html")
