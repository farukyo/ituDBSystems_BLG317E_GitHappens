from flask import Flask
from flask_login import LoginManager
from sqlalchemy import text
from database.db import engine
from admin import admin_bp
from routes import main_bp, auth_bp, user_bp, movie_bp, series_bp, episode_bp, celebrity_bp
from routes.auth_routes import User 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this_later'

# Blueprint kayıtları (Orijinal haliyle korundu)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(movie_bp)
app.register_blueprint(series_bp)
app.register_blueprint(episode_bp)
app.register_blueprint(celebrity_bp)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login'in kullanıcıyı her sayfa geçişinde MySQL'den tanımasını sağlar."""
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": user_id}).fetchone()
        if result:
            u = result._mapping
            return User(
                id=u['id'], username=u['username'], email=u['email'], 
                password_hash=u['password_hash'], dob=u['dob'], 
                gender=u['gender'], is_admin=u['is_admin']
            )
    return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)