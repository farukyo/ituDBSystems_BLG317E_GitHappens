# Main Application Entry Point
# Initializes Flask app, registers blueprints, and configures Flask-Login.
# All routes are modularized in the 'routes' package.

from flask import Flask
from flask_login import LoginManager
from admin import admin_bp
from routes import main_bp, auth_bp, user_bp, movie_bp, series_bp, episode_bp, celebrity_bp
from routes.auth_routes import load_user_by_id

# --- App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this_later'

# --- Blueprint Registration ---
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(movie_bp)
app.register_blueprint(series_bp)
app.register_blueprint(episode_bp)
app.register_blueprint(celebrity_bp)

# --- Login Manager Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'


@login_manager.user_loader
def load_user(user_id):
    """Tells Flask-Login how to load a user from the mock DB."""
    return load_user_by_id(user_id)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)