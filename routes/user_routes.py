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
    entity_type = request.form.get('entity_type') # 'movie', 'series', 'episode', 'person'
    user_id = current_user.id
    
    if not entity_id or not entity_type:
        return "Error: Missing Data", 400

    # Hangi tabloyu kullanacağımızı seçiyoruz
    if entity_type == 'person':
        table_name = "user_likes_people"
        col_name = "people_id"
    else:
        # movie, series, episode hepsi 'titles' tablosuna gider
        table_name = "user_likes_titles"
        col_name = "title_id"

    with engine.connect() as conn:
        # 1. Kontrol Et
        # Not: Artık entity_type kontrolüne gerek yok çünkü tablolar ayrıldı
        check_sql = f"SELECT 1 FROM githappens_users.{table_name} WHERE user_id = :uid AND {col_name} = :eid"
        
        result = conn.execute(text(check_sql), {"uid": user_id, "eid": entity_id}).fetchone()
        
        if result:
            # 2. Varsa SİL (Unlike)
            delete_sql = f"DELETE FROM githappens_users.{table_name} WHERE user_id = :uid AND {col_name} = :eid"
            conn.execute(text(delete_sql), {"uid": user_id, "eid": entity_id})
        else:
            # 3. Yoksa EKLE (Like)
            insert_sql = f"INSERT INTO githappens_users.{table_name} (user_id, {col_name}) VALUES (:uid, :eid)"
            conn.execute(text(insert_sql), {"uid": user_id, "eid": entity_id})
            
        conn.commit()

    return "1"

@user_bp.route("/profile")
@login_required
def profile():
    uid = current_user.id
    
    liked_movies = []
    liked_series = []
    liked_episodes = []
    liked_celebs = []
    percentile = 100
    
    with engine.connect() as conn:
        # Get user's current score
        user_score_res = conn.execute(text("SELECT score FROM githappens_users.users WHERE id = :uid"), {"uid": uid}).fetchone()
        user_score = user_score_res[0] if user_score_res else 0

        # Calculate Percentile (Top X%)
        total_users = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users")).scalar()
        higher_scores = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users WHERE score > :s"), {"s": user_score}).scalar()
        if total_users > 0:
            # Rank = higher_scores + 1. Top % = (Rank / Total) * 100
            percentile = ((higher_scores + 1) / total_users) * 100

        # A. Beğenilen FİLMLER (user_likes_titles tablosundan)
        sql_mov = """
            SELECT m.movieId, m.movieTitle, m.startYear, r.averageRating
            FROM movies m
            JOIN githappens_users.user_likes_titles ul ON m.movieId = ul.title_id
            LEFT JOIN ratings r ON m.movieId = r.titleId
            WHERE ul.user_id = :uid 
            -- Filmleri ayırt etmek için ID yapısına bakıyoruz veya join ile veri geliyorsa zaten filmdir
            AND m.movieId LIKE 'tt%' 
        """
        liked_movies = conn.execute(text(sql_mov), {"uid": uid}).fetchall()

        # B. Beğenilen DİZİLER (user_likes_titles tablosundan)
        sql_ser = """
            SELECT s.seriesId, s.seriesTitle, s.startYear, s.endYear
            FROM series s
            JOIN githappens_users.user_likes_titles ul ON s.seriesId = ul.title_id
            WHERE ul.user_id = :uid
        """
        liked_series = conn.execute(text(sql_ser), {"uid": uid}).fetchall()
        
        # C. Beğenilen BÖLÜMLER (user_likes_titles tablosundan)
        sql_ep = """
            SELECT e.episodeId, e.epTitle, s.seriesTitle, e.seNumber, e.epNumber, s.seriesId
            FROM Episode e
            JOIN Series s ON e.seriesId = s.seriesId
            JOIN githappens_users.user_likes_titles ul ON e.episodeId = ul.title_id
            WHERE ul.user_id = :uid
        """
        liked_episodes = conn.execute(text(sql_ep), {"uid": uid}).fetchall()

        # D. Beğenilen ÜNLÜLER (user_likes_people tablosundan - BURASI DEĞİŞTİ)
        sql_cel = """
            SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear
            FROM people p
            JOIN githappens_users.user_likes_people ul ON p.peopleId = ul.people_id
            WHERE ul.user_id = :uid
        """
        liked_celebs = conn.execute(text(sql_cel), {"uid": uid}).fetchall()

    return render_template("profile.html", 
                           user=current_user, 
                           score=user_score,
                           liked_movies=liked_movies,
                           liked_series=liked_series,
                           liked_episodes=liked_episodes,
                           liked_celebs=liked_celebs,
                           percentile=round(percentile, 1))