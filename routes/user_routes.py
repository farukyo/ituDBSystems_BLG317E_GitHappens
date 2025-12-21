# User Routes Module
from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text
from database.db import engine

user_bp = Blueprint('user', __name__)

@user_bp.route("/like_entity", methods=["POST"])
@login_required
def like_entity():
    entity_id = request.form.get('entity_id')
    entity_type = request.form.get('entity_type') 
    user_id = current_user.id
    
    if not entity_id or not entity_type:
        return "Error: Missing Data", 400

    
    if entity_type == 'person':
        table_name = "user_likes_people"
        col_name = "people_id"
    else:
        
        table_name = "user_likes_titles"
        col_name = "title_id"

    with engine.connect() as conn:

        check_sql = f"SELECT 1 FROM githappens_users.{table_name} WHERE user_id = :uid AND {col_name} = :eid"
        
        result = conn.execute(text(check_sql), {"uid": user_id, "eid": entity_id}).fetchone()
        
        if result:
            
            delete_sql = f"DELETE FROM githappens_users.{table_name} WHERE user_id = :uid AND {col_name} = :eid"
            conn.execute(text(delete_sql), {"uid": user_id, "eid": entity_id})
        else:
            
            insert_sql = f"INSERT INTO githappens_users.{table_name} (user_id, {col_name}) VALUES (:uid, :eid)"
            conn.execute(text(insert_sql), {"uid": user_id, "eid": entity_id})
            
        conn.commit()

    return "1"

@user_bp.route("/profile")
@user_bp.route("/profile/<int:user_id>")
@login_required
def profile(user_id=None):
    
    target_uid = user_id if user_id else current_user.id
    
    liked_movies = []
    liked_series = []
    liked_episodes = []
    liked_celebs = []
    percentile = 100
    
    with engine.connect() as conn:
        
        user_res = conn.execute(text("SELECT id, username, email, dob, gender, score FROM githappens_users.users WHERE id = :uid"), {"uid": target_uid}).fetchone()
        
        if not user_res:
            from flask import flash, redirect, url_for
            flash("User not found.")
            return redirect(url_for('main.index'))

        user_score = user_res.score if user_res.score else 0

        # Calculate Percentile (Top X%)
        total_users = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users")).scalar()
        at_or_above = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users WHERE score >= :s"), {"s": user_score}).scalar()
        if total_users > 0:
            percentile = (at_or_above / total_users) * 100

        
        sql_mov = """
            SELECT m.movieId, m.movieTitle, m.startYear, r.averageRating
            FROM movies m
            JOIN githappens_users.user_likes_titles ul ON m.movieId = ul.title_id
            LEFT JOIN ratings r ON m.movieId = r.titleId
            WHERE ul.user_id = :uid 
            AND m.movieId LIKE 'tt%' 
        """
        liked_movies = conn.execute(text(sql_mov), {"uid": target_uid}).fetchall()

        
        sql_ser = """
            SELECT s.seriesId, s.seriesTitle, s.startYear, s.endYear
            FROM series s
            JOIN githappens_users.user_likes_titles ul ON s.seriesId = ul.title_id
            WHERE ul.user_id = :uid
        """
        liked_series = conn.execute(text(sql_ser), {"uid": target_uid}).fetchall()
        
        
        sql_ep = """
            SELECT e.episodeId, e.epTitle, s.seriesTitle, e.seNumber, e.epNumber, s.seriesId
            FROM Episode e
            JOIN Series s ON e.seriesId = s.seriesId
            JOIN githappens_users.user_likes_titles ul ON e.episodeId = ul.title_id
            WHERE ul.user_id = :uid
        """
        liked_episodes = conn.execute(text(sql_ep), {"uid": target_uid}).fetchall()

        
        sql_cel = """
            SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear
            FROM people p
            JOIN githappens_users.user_likes_people ul ON p.peopleId = ul.people_id
            WHERE ul.user_id = :uid
        """
        liked_celebs = conn.execute(text(sql_cel), {"uid": target_uid}).fetchall()

    return render_template("profile.html", 
                           user=user_res, 
                           score=user_score,
                           liked_movies=liked_movies,
                           liked_series=liked_series,
                           liked_episodes=liked_episodes,
                           liked_celebs=liked_celebs,
                           percentile=round(percentile, 1),
                           is_own_profile=(target_uid == current_user.id))