from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp

# SADECE LİSTELEME VE ÇÖZÜLDÜ TİKLEME

@admin_bp.route("/suggestions", methods=["GET", "POST"])
def suggestion_list():
    with engine.connect() as conn:
        suggestions = conn.execute(
            text("""
                SELECT 
                    s.suggestion_id,
                    u.username,
                    s.subject,
                    s.suggestion_text,
                    s.created_at,
                    s.is_resolved
                FROM githappens_users.user_suggestions s
                JOIN githappens_users.users u ON s.user_id = u.id
                ORDER BY s.created_at DESC
            """)
        ).mappings().all()
    return render_template("admin/suggestion_list.html", suggestions=suggestions)

@admin_bp.route("/suggestions/toggle/<int:suggestion_id>", methods=["POST"])
def suggestion_toggle(suggestion_id):
    with engine.begin() as conn:
        current = conn.execute(
            text("SELECT is_resolved FROM githappens_users.user_suggestions WHERE suggestion_id = :id"),
            {"id": suggestion_id}
        ).fetchone()
        if not current:
            flash("Suggestion not found.")
            return redirect(url_for("admin.suggestion_list"))
        new_status = 0 if current[0] == 1 else 1
        conn.execute(
            text("UPDATE githappens_users.user_suggestions SET is_resolved = :status WHERE suggestion_id = :id"),
            {"status": new_status, "id": suggestion_id}
        )
    return redirect(url_for("admin.suggestion_list"))