from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database.db import engine
from sqlalchemy import text
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import text
#from database import engine 
# --- App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this_later' 

# --- Login Manager Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# --- MOCK USER SYSTEM (No Database) ---

MOCK_USERS_DB = {}
USER_ID_COUNTER = 0

class User(UserMixin):
    """
    A mock User class for Flask-Login.
    """
    # UPDATED: Changed 'age' to 'dob'
    def __init__(self, id, username, email, password_hash, dob=None, gender=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash 
        
        # NEW: Store new data
        self.dob = dob
        self.gender = gender
        
        # Data for the profile page
        self.quiz_score = 0
        self.liked_movies = []
        self.liked_series = []
        self.liked_actors = [] 

    def check_password(self, password):
        return self.password_hash == password

@login_manager.user_loader
def load_user(user_id):
    """Tells Flask-Login how to load a user from the mock DB."""
    return MOCK_USERS_DB.get(int(user_id))

# --- END MOCK USER SYSTEM ---


# --- Main Routes ---
# (index, about, quiz, recommend, movies, series, etc. are unchanged)
@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/quiz")
@login_required 
def quiz():
    return render_template("quiz.html")

@app.route("/recommend")
@login_required 
def recommend():
    return render_template("recommend.html")

@app.route("/movies")

def movies():
    search_query = request.args.get('q')
    genre_filter = request.args.get('genre')
    with engine.connect() as conn:
        sql = "SELECT * FROM movies WHERE 1=1"
        params = {}

        if search_query:
            sql += " AND movieTitle LIKE :q"
            params["q"] = f"%{search_query}%"
        # Genre filtresi
        if genre_filter:
            sql += " AND genres LIKE :genre"
            params["genre"] = f"%{genre_filter}%"
        # Limit ekle
        sql += " LIMIT 100;"
        result = conn.execute(text(sql), params)
        data = result.fetchall()
    # Title
    if search_query:
        page_title = f"Results for '{search_query}'"
    else:
        page_title = "All Movies"
    return render_template("movies.html", items=data, title=page_title)

# --- Movie Detail Route ---
@app.route("/movie/<movie_id>")
def movie(movie_id):
    with engine.connect() as conn:
        # Filmin temel bilgilerini çekin
        sql = """
            SELECT movieId, movieTitle, titleType, startYear, runtimeMinutes
            FROM movies
            WHERE movieId = :movieId
        """
        result = conn.execute(text(sql), {"movieId": movie_id})
        movie = result.fetchone()
        
        if not movie:
            flash(f"Movie with ID {movie_id} not found.")
            return redirect(url_for('movies'))
        
        # O filmde yer alan oyuncuları ve rolleri çekin (principals tablosu kullanarak)
        cast_sql = """
            SELECT p.peopleId, p.primaryName, pr.category, pr.characters
            FROM principals pr
            JOIN people p ON pr.peopleId = p.peopleId
            WHERE pr.titleId = :movieId
            ORDER BY pr.category, p.primaryName
        """
        cast_result = conn.execute(text(cast_sql), {"movieId": movie_id})
        cast = cast_result.fetchall()
        
    # Sayfa başlığını filmin adına göre ayarlıyoruz (istediğiniz gibi)
    page_title = f"{movie.movieTitle} ({movie.startYear})"
    
    return render_template("movie.html", 
                           movie=movie, 
                           cast=cast, 
                           title=page_title)

@app.route("/series")
def series():
    series_data = [
        {"title": "Breaking Bad"},
        {"title": "Game of Thrones"},
    ]
    return render_template("series.html", series_list=series_data)

@app.route("/characters")
def characters():
    return render_template("characters.html")

@app.route("/episodes")
def episodes():
    # URL'den parametreleri al
    ep_title = request.args.get('epTitle')
    runtime_min = request.args.get('runtimeMin')
    runtime_max = request.args.get('runtimeMax')
    series_name = request.args.get('seriesName')
    season_number = request.args.get('seNumber')
    episode_number = request.args.get('epNumber')
    
    with engine.connect() as conn:
        sql = """
            SELECT e.episodeId, e.epTitle, e.runtimeMinutes, 
                   e.seriesId, e.seNumber, e.epNumber,
                   s.seriesTitle
            FROM Episode e
            LEFT JOIN Series s ON e.seriesId = s.seriesId
            WHERE 1=1
        """
        params = {}
        
        # Episode Title filtresi
        if ep_title:
            sql += " AND e.epTitle LIKE :epTitle"
            params["epTitle"] = f"%{ep_title}%"
        
        # Runtime filtresi (min)
        if runtime_min:
            sql += " AND e.runtimeMinutes >= :runtimeMin"
            params["runtimeMin"] = int(runtime_min)
        
        # Runtime filtresi (max)
        if runtime_max:
            sql += " AND e.runtimeMinutes <= :runtimeMax"
            params["runtimeMax"] = int(runtime_max)
        
        # Series Name filtresi
        if series_name:
            sql += " AND s.seriesTitle LIKE :seriesName"
            params["seriesName"] = f"%{series_name}%"
        
        # Season Number filtresi
        if season_number:
            sql += " AND e.seNumber = :seNumber"
            params["seNumber"] = int(season_number)
        
        # Episode Number filtresi
        if episode_number:
            sql += " AND e.epNumber = :epNumber"
            params["epNumber"] = int(episode_number)
        
        sql += " LIMIT 100"
        
        # SQL sorgusunu göstermek için parametreleri yerleştir
        display_sql = sql
        for key, value in params.items():
            if isinstance(value, str):
                display_sql = display_sql.replace(f":{key}", f"'{value}'")
            else:
                display_sql = display_sql.replace(f":{key}", str(value))
        
        result = conn.execute(text(sql), params)
        data = result.fetchall()
    
    title = "Episodes"
    if ep_title:
        title = f"Episodes matching '{ep_title}'"
    
    return render_template("episodes.html", items=data, title=title, sql_query=display_sql)


@app.route("/episode/<episode_id>")
def episode_detail(episode_id):
    with engine.connect() as conn:
        # Episode bilgileri
        sql = """
            SELECT e.episodeId, e.epTitle, e.runtimeMinutes, 
                   e.seriesId, e.seNumber, e.epNumber,
                   s.seriesTitle, s.startYear, s.endYear
            FROM Episode e
            LEFT JOIN Series s ON e.seriesId = s.seriesId
            WHERE e.episodeId = :episodeId
        """
        result = conn.execute(text(sql), {"episodeId": episode_id})
        episode = result.fetchone()
        
        if not episode:
            flash("Episode not found.")
            return redirect(url_for('episodes'))
        
        # Dizinin genre'ları
        genres_sql = """
            SELECT g.genreName
            FROM Series_Genres sg
            JOIN genres g ON sg.genreId = g.genreId
            WHERE sg.seriesId = :seriesId
        """
        genres_result = conn.execute(text(genres_sql), {"seriesId": episode.seriesId})
        genres = [row.genreName for row in genres_result.fetchall()]
        
        # Dizide toplam kaç sezon ve bölüm var
        stats_sql = """
            SELECT 
                COUNT(DISTINCT seNumber) as total_seasons,
                COUNT(*) as total_episodes
            FROM Episode
            WHERE seriesId = :seriesId
        """
        stats_result = conn.execute(text(stats_sql), {"seriesId": episode.seriesId})
        stats = stats_result.fetchone()
        
        # Bu bölümdeki oyuncular/ekip (principals tablosundan)
        cast_sql = """
            SELECT p.peopleId, p.primaryName, pr.category, pr.characters,
                   prof.professionName
            FROM principals pr
            JOIN people p ON pr.peopleId = p.peopleId
            LEFT JOIN profession prof ON p.professionId = prof.professionId
            WHERE pr.titleId = :episodeId
            ORDER BY pr.category
        """
        cast_result = conn.execute(text(cast_sql), {"episodeId": episode_id})
        cast = cast_result.fetchall()
    
    return render_template("episode.html", 
                           episode=episode, 
                           genres=genres,
                           stats=stats,
                           cast=cast)


    
@app.route("/celebrities")
def celebrities():
    # 1. URL'den Parametreleri Al
    search_query = request.args.get('q')
    profession_list = request.args.getlist('profession')
    primary_letter = request.args.get('primary_name') # HTML'deki name="primary_name"
    birth_filter = request.args.get('birth_year')
    death_filter = request.args.get('death_year')
    order_filter = request.args.get('order_by')

    with engine.connect() as conn:
        sql = """
            SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear, pr.professionName 
            FROM people p
            LEFT JOIN profession pr ON p.professionId = pr.professionId
            WHERE 1=1
        """
        params = {}


        if not search_query and not primary_letter:
            sql += " AND p.primaryName REGEXP '^[A-Za-z]'"
            sql += " AND CHAR_LENGTH(p.primaryName) >= 3"
            sql += " AND p.primaryName REGEXP '[A-Za-z]{2,}'"
            sql += " AND p.primaryName NOT REGEXP '^[A-Za-z][ ._$/0-9\\'-]'"
    
        if search_query:
            sql += " AND p.primaryName LIKE :q"
            params["q"] = f"%{search_query}%"

        if profession_list:
            prof_conditions = []
            for i, prof in enumerate(profession_list):
                key = f"prof_{i}" 
                prof_conditions.append(f"pr.professionName LIKE :{key}")
                params[key] = f"%{prof}%"
            sql += " AND (" + " AND ".join(prof_conditions) + ")"
            
        if primary_letter:
            sql += " AND p.primaryName LIKE :letter"
            params["letter"] = f"{primary_letter}%"

        if birth_filter:
            sql += " AND p.birthYear = :byear"
            params["byear"] = int(birth_filter)

        if death_filter:
            sql += " AND p.deathYear = :dyear"
            params["dyear"] = int(death_filter)

        if order_filter == "alphabetical":
            sql += " ORDER BY p.primaryName ASC"
        
        elif order_filter == "age-asc":
            sql += """ 
                ORDER BY (
                    CASE 
                        WHEN p.deathYear IS NOT NULL THEN (p.deathYear - p.birthYear)
                        ELSE (2025 - p.birthYear)
                    END
                ) ASC
            """
        
        elif order_filter == "age-desc":
             sql += """ 
                ORDER BY (
                    CASE 
                        WHEN p.deathYear IS NOT NULL THEN (p.deathYear - p.birthYear)
                        ELSE (2025 - p.birthYear)
                    END
                ) DESC
            """
        else:
            sql += " ORDER BY p.primaryName ASC"

        sql += " LIMIT 50"

        result = conn.execute(text(sql), params)
        data = result.fetchall()

    title = f"Results for '{search_query}'" if search_query else "Celebrities"
    return render_template("celebrities.html", items=data, title=title)

@app.route("/suggest", methods=["GET", "POST"])
@login_required
def suggest():
    if request.method == "POST":
        subject = request.form.get("subject")
        message_body = request.form.get("message")
        
        # Gönderen kişinin bilgileri
        user_email = current_user.email
        user_name = current_user.username
        
        # -------------------------------------------------------
        # MAİL GÖNDERME KISMI BURAYA GELECEK
        # (İleride buraya SMTP veya API kodları eklenecek)
        # -------------------------------------------------------
        
        flash("Thank you! Your suggestion has been sent successfully.")
        return redirect(url_for('index'))
        
    return render_template("suggestion.html")

# --- Authentication Routes ---

@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        user_to_login = None
        for user in MOCK_USERS_DB.values():
            if user.email == email:
                user_to_login = user
                break
        
        if user_to_login and user_to_login.check_password(password):
            login_user(user_to_login)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    global USER_ID_COUNTER 
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        
        # UPDATED: Get 'dob' from form
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        
        for user in MOCK_USERS_DB.values():
            if user.email == email:
                flash("Email already exists.")
                return redirect(url_for('signup'))

        # Create new user
        USER_ID_COUNTER += 1
        
        # UPDATED: Pass 'dob' to the User object
        new_user = User(
            id=USER_ID_COUNTER,
            username=username,
            email=email,
            password_hash=password,
            dob=dob,
            gender=gender
        )
        MOCK_USERS_DB[new_user.id] = new_user
        
        login_user(new_user)
        return redirect(url_for('index'))

    return render_template("signup.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- User Profile Route ---

@app.route("/profile")
@login_required 
def profile():
    return render_template("profile.html", user=current_user)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)