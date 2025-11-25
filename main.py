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
            sql += " AND primaryTitle LIKE :q"
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
    return render_template("episodes.html")

@app.route("/names")
def names_page():
    search_query = request.args.get('q')  # Arama terimini al

    with engine.connect() as conn:
        if search_query:
            # İsimlerde arama yap (primaryName sütunu)
            sql_query = text("SELECT * FROM names WHERE primaryName LIKE :term LIMIT 100")
            result = conn.execute(sql_query, {"term": f"%{search_query}%"})
            page_title = f"'{search_query}' için Kişi Sonuçları"
        else:
            # Arama yoksa ilk 50 kişiyi getir
            sql_query = text("SELECT * FROM names LIMIT 50")
            result = conn.execute(sql_query)
            page_title = "Tüm Oyuncular ve Çalışanlar"

        data = result.fetchall()
        # names.html sayfasına gönderiyoruz
        return render_template("names.html", items=data, title=page_title)
    
@app.route("/celebrities")
def celebrities():
    return render_template("celebrities.html")
def api_celebrities():
    name_query = request.args.get("q")
    profession = request.args.get("profession")
    primary_letter = request.args.get("primary_letter")
    birth_year = request.args.get("birth_year")
    death_year = request.args.get("death_year")
    order_by = request.args.get("order_by")

    sql = "SELECT * FROM people WHERE 1=1"
    params = {}

    # Search (name)
    if name_query:
        sql += " AND primaryName LIKE :name"
        params["name"] = f"%{name_query}%"

    # Profession filter
    if profession:
        sql += " AND primaryProfession LIKE :prof"
        params["prof"] = f"%{profession}%"

    # Starts with A/B/C ...
    if primary_letter:
        sql += " AND primaryName LIKE :letter"
        params["letter"] = f"{primary_letter}%"

    # Birth year filter
    if birth_year:
        sql += " AND birthYear LIKE :byear"
        params["byear"] = f"{birth_year}%"

    # Death year filter
    if death_year == "alive":
        sql += " AND deathYear IS NULL"
    elif death_year:
        sql += " AND deathYear >= :dyear"
        params["dyear"] = death_year

    # Sorting
    if order_by == "alphabetical":
        sql += " ORDER BY primaryName ASC"
    elif order_by == "age-asc":
        sql += " ORDER BY birthYear ASC"
    elif order_by == "popularity":
        sql += " ORDER BY popularity DESC"

    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        data = [dict(row) for row in result]

    return jsonify(data)

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