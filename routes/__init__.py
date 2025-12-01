# Routes package initialization
# This module exports all route blueprints for the Flask application.

from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.movie_routes import movie_bp
from routes.series_routes import series_bp
from routes.episode_routes import episode_bp
from routes.celebrity_routes import celebrity_bp

__all__ = ['main_bp', 'auth_bp', 'user_bp', 'movie_bp', 'series_bp', 'episode_bp', 'celebrity_bp']
