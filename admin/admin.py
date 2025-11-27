from flask import Blueprint, render_template
from sqlalchemy import text
from database.db import engine

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/")
def admin_home():
    return "Admin Panel Home"

@admin_bp.route("/users")
def users():
    with engine.connect() as conn:
        data = conn.execute(text("SELECT * FROM users LIMIT 20")).fetchall()
    return render_template("admin_users.html", users=data)