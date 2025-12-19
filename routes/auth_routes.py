from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import text
from database.db import engine # Veritabanı bağlantısı

auth_bp = Blueprint('auth', __name__)

class User(UserMixin):
    """Flask-Login için MySQL ile uyumlu User modeli."""
    def __init__(self, id, username, email, password_hash, dob=None, gender=None, is_admin=False):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.dob = dob
        self.gender = gender
        self.is_admin = bool(is_admin)
        # Orijinal değişkenlerini koruyoruz
        self.quiz_score = 0
        self.liked_movies = []
        self.liked_series = []
        self.liked_actors = []

    def check_password(self, password):
        return self.password_hash == password

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT * FROM users WHERE email = :email"), 
                {"email": email}
            ).fetchone()
            
            if result:
                u = result._mapping
                user_obj = User(
                    id=u['id'], username=u['username'], email=u['email'], 
                    password_hash=u['password_hash'], dob=u['dob'], 
                    gender=u['gender'], is_admin=u['is_admin']
                )
                
                if user_obj.check_password(password):
                    login_user(user_obj)
                    next_page = request.args.get('next')
                    return redirect(next_page or url_for('main.index'))
            
            flash("Invalid email or password.")
    return render_template("login.html")

@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        
        with engine.connect() as conn:
            # Email kontrolü
            existing = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
            if existing:
                flash("Email already exists.")
                return redirect(url_for('auth.signup'))

            # Kayıt (ID AUTO_INCREMENT olduğu için eklemiyoruz)
            conn.execute(text("""
                INSERT INTO users (username, email, password_hash, dob, gender) 
                VALUES (:u, :e, :p, :d, :g)
            """), {"u": username, "e": email, "p": password, "d": dob, "g": gender})
            conn.commit()
            
            # Kayıt sonrası otomatik login için kullanıcıyı tekrar çekiyoruz
            u = conn.execute(text("SELECT * FROM users WHERE email = :email"), {"email": email}).fetchone()._mapping
            new_user = User(id=u['id'], username=u['username'], email=u['email'], password_hash=u['password_hash'])
            login_user(new_user)
            return redirect(url_for('main.index'))

    return render_template("signup.html")

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))