from flask import Flask, redirect, url_for, request, flash
from flask_login import LoginManager, current_user
from sqlalchemy import text
from database.db import engine
from admin import admin_bp
from routes import main_bp, auth_bp, user_bp, movie_bp, series_bp, episode_bp, celebrity_bp
from routes.auth_routes import User 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_super_secret_key_change_this_later'

# Blueprint kayıtları
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
    with engine.connect() as conn:
        sql = text("SELECT * FROM githappens_users.users WHERE id = :id")
        result = conn.execute(sql, {"id": user_id}).fetchone()
        if result:
            u = result._mapping
            return User(
                id=u['id'], username=u['username'], email=u['email'], 
                password_hash=u['password_hash'], dob=u['dob'], 
                gender=u['gender'], is_admin=u['is_admin'],
                score=u.get('score', 0)
            )
    return None


# Admin erişim kontrolü
@app.before_request
def check_admin_access():
    """Admin sayfalarına erişim kontrolü"""
    if request.path.startswith('/admin'):
        if not current_user.is_authenticated:
            flash("You need to log in to access the admin panel.", "warning")
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash("You do not have permission to access the admin panel. Only administrators can access this area.", "error")
            return redirect(url_for('main.index'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)