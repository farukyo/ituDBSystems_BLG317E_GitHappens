# Authentication Routes Module
# Handles user login, signup, logout, and user session management.
# Also contains User model and mock database for simplicity.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user

auth_bp = Blueprint('auth', __name__)

# --- User Model and Mock Database ---

MOCK_USERS_DB = {}
_USER_ID_COUNTER = 0


def get_next_user_id():
    """Generate and return the next available user ID."""
    global _USER_ID_COUNTER
    _USER_ID_COUNTER += 1
    return _USER_ID_COUNTER


def load_user_by_id(user_id):
    """Load a user from the mock database by ID."""
    return MOCK_USERS_DB.get(int(user_id))


class User(UserMixin):
    """User class for Flask-Login authentication."""
    
    def __init__(self, id, username, email, password_hash, dob=None, gender=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.dob = dob
        self.gender = gender
        self.quiz_score = 0
        self.liked_movies = []
        self.liked_series = []
        self.liked_actors = []

    def check_password(self, password):
        return self.password_hash == password


# --- Routes ---

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
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
            return redirect(next_page or url_for('main.index'))
        else:
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
        
        for user in MOCK_USERS_DB.values():
            if user.email == email:
                flash("Email already exists.")
                return redirect(url_for('auth.signup'))

        # Create new user
        new_user_id = get_next_user_id()
        
        new_user = User(
            id=new_user_id,
            username=username,
            email=email,
            password_hash=password,
            dob=dob,
            gender=gender
        )
        MOCK_USERS_DB[new_user.id] = new_user
        
        login_user(new_user)
        return redirect(url_for('main.index'))

    return render_template("signup.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
