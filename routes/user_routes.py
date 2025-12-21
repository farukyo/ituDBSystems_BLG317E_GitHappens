# User Routes Module
from flask import Blueprint, jsonify, render_template, request
from flask_login import login_required, current_user
from sqlalchemy import text
from database.db import engine

user_bp = Blueprint('user', __name__)

# --- 1. EVRENSEL BEĞENME (LIKE) FONKSİYONU ---
# Frontend ile uyumlu olması için '/like_entity' rotasını kullanıyoruz.
@user_bp.route("/like_entity", methods=["POST"])
@login_required
def like_entity():
    # JavaScript'ten (FormData) gelen verileri al
    entity_id = request.form.get('entity_id')
    entity_type = request.form.get('entity_type') # 'movie', 'series', 'episode', 'person'
    user_id = current_user.id
    
    if not entity_id or not entity_type:
        return "Error: Missing Data", 400

    with engine.connect() as conn:
        # 1. Kontrol Et: Bu kullanıcı bunu daha önce beğenmiş mi?
        check_sql = """
            SELECT 1 FROM githappens_users.user_likes 
            WHERE user_id = :uid AND entity_id = :eid AND entity_type = :etype
        """
        result = conn.execute(text(check_sql), {"uid": user_id, "eid": entity_id, "etype": entity_type}).fetchone()
        
        if result:
            # 2. Varsa SİL (Unlike - Vazgeç)
            delete_sql = """
                DELETE FROM githappens_users.user_likes 
                WHERE user_id = :uid AND entity_id = :eid AND entity_type = :etype
            """
            conn.execute(text(delete_sql), {"uid": user_id, "eid": entity_id, "etype": entity_type})
        else:
            # 3. Yoksa EKLE (Like - Beğen)
            insert_sql = """
                INSERT INTO githappens_users.user_likes (user_id, entity_id, entity_type)
                VALUES (:uid, :eid, :etype)
            """
            conn.execute(text(insert_sql), {"uid": user_id, "eid": entity_id, "etype": entity_type})
            
        conn.commit()

    # Başarılı olduğunda frontend'in beklediği "1" cevabını döndür
    return "1"


# --- 2. PROFIL SAYFASI (Tüm Verileri Çekme) ---
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

        # Calculate Percentile
        total_users = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users")).scalar()
        higher_scores = conn.execute(text("SELECT COUNT(*) FROM githappens_users.users WHERE score > :s"), {"s": user_score}).scalar()
        if total_users > 0:
            percentile = (higher_scores / total_users) * 100

        # A. Beğenilen FİLMLERİ Çek
        sql_mov = """
            SELECT m.movieId, m.movieTitle, m.startYear, r.averageRating
            FROM movies m
            JOIN githappens_users.user_likes ul ON m.movieId = ul.entity_id
            LEFT JOIN ratings r ON m.movieId = r.titleId
            WHERE ul.user_id = :uid AND ul.entity_type = 'movie'
        """
        liked_movies = conn.execute(text(sql_mov), {"uid": uid}).fetchall()

        # B. Beğenilen DİZİLERİ Çek
        sql_ser = """
            SELECT s.seriesId, s.seriesTitle, s.startYear, s.endYear
            FROM series s
            JOIN githappens_users.user_likes ul ON s.seriesId = ul.entity_id
            WHERE ul.user_id = :uid AND ul.entity_type = 'series'
        """
        liked_series = conn.execute(text(sql_ser), {"uid": uid}).fetchall()
        
        # C. Beğenilen BÖLÜMLERİ Çek
        sql_ep = """
            SELECT e.episodeId, e.epTitle, s.seriesTitle, e.seNumber, e.epNumber, s.seriesId
            FROM Episode e
            JOIN Series s ON e.seriesId = s.seriesId
            JOIN githappens_users.user_likes ul ON e.episodeId = ul.entity_id
            WHERE ul.user_id = :uid AND ul.entity_type = 'episode'
        """
        liked_episodes = conn.execute(text(sql_ep), {"uid": uid}).fetchall()

        # D. Beğenilen ÜNLÜLERİ Çek
        sql_cel = """
            SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear
            FROM people p
            JOIN githappens_users.user_likes ul ON p.peopleId = ul.entity_id
            WHERE ul.user_id = :uid AND ul.entity_type = 'person'
        """
        liked_celebs = conn.execute(text(sql_cel), {"uid": uid}).fetchall()

    # HTML'e tüm listeleri gönder
    return render_template("profile.html", 
                           user=current_user, 
                           liked_movies=liked_movies,
                           liked_series=liked_series,
                           liked_episodes=liked_episodes,
                           liked_celebs=liked_celebs,
                           percentile=round(percentile, 1))