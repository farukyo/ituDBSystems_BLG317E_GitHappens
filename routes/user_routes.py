# User Routes Module
# Handles user profile page and user-specific features.
from flask import Blueprint, jsonify,render_template
from flask_login import login_required, current_user
from sqlalchemy import text
from database.db import engine

user_bp = Blueprint('user', __name__)

# --- BU KISIM EKLENMELİ ---
@user_bp.route("/like/<entity_type>/<entity_id>", methods=["POST"])
@login_required
def toggle_like(entity_type, entity_id):
    with engine.connect() as conn:
        # 1. Zaten var mı bak?
        check_sql = text("""
            SELECT 1 FROM githappens_users.user_likes 
            WHERE user_id = :uid AND entity_id = :eid AND entity_type = :etype
        """)
        existing = conn.execute(check_sql, {
            "uid": current_user.id, "eid": entity_id, "etype": entity_type
        }).fetchone()

        if existing:
            # 2. Varsa SİL (Unlike)
            conn.execute(text("DELETE FROM githappens_users.user_likes WHERE user_id = :uid AND entity_id = :eid AND entity_type = :etype"),
                         {"uid": current_user.id, "eid": entity_id, "etype": entity_type})
            conn.commit()
            return jsonify({"status": "unliked"})
        else:
            # 3. Yoksa EKLE (Like)
            conn.execute(text("INSERT INTO githappens_users.user_likes (user_id, entity_id, entity_type) VALUES (:uid, :eid, :etype)"),
                         {"uid": current_user.id, "eid": entity_id, "etype": entity_type})
            conn.commit()
            return jsonify({"status": "liked"})
        
        
@user_bp.route("/profile")
@login_required
def profile():
    liked_celebs = []
    
    with engine.connect() as conn:
        sql = """
            SELECT p.peopleId, p.primaryName
            FROM people p
            JOIN githappens_users.user_likes ul ON p.peopleId = ul.entity_id
            WHERE ul.user_id = :uid 
              AND ul.entity_type = 'person'
        """
        result = conn.execute(text(sql), {"uid": current_user.id})
        liked_celebs = result.fetchall()

    return render_template("profile.html", user=current_user, liked_celebs=liked_celebs)

