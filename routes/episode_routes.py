# Episode Routes Module
# Handles episode listing and detail pages with advanced filtering options.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from flask_login import current_user
from database.db import engine

episode_bp = Blueprint('episode', __name__)


@episode_bp.route("/episodes")
def episodes():
    ep_title = request.args.get('epTitle')
    runtime_min = request.args.get('runtimeMin')
    runtime_max = request.args.get('runtimeMax')
    series_name = request.args.get('seriesName')
    season_number = request.args.get('seNumber')
    episode_number = request.args.get('epNumber')
    uid = current_user.id if current_user.is_authenticated else -1
    with engine.connect() as conn:
        sql = """
            SELECT e.episodeId, e.epTitle, e.runtimeMinutes, 
                   e.seriesId, e.seNumber, e.epNumber,
                   s.seriesTitle,
                   CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked  
            FROM Episode e
            LEFT JOIN Series s ON e.seriesId = s.seriesId
            LEFT JOIN githappens_users.user_likes_titles ul ON e.episodeId = ul.title_id AND ul.user_id = :uid
            WHERE 1=1
        """
        params = {"uid": uid}
        
        if ep_title:
            sql += " AND e.epTitle LIKE :epTitle"
            params["epTitle"] = f"%{ep_title}%"
        
        if runtime_min:
            sql += " AND e.runtimeMinutes >= :runtimeMin"
            params["runtimeMin"] = int(runtime_min)
        
        if runtime_max:
            sql += " AND e.runtimeMinutes <= :runtimeMax"
            params["runtimeMax"] = int(runtime_max)
        
        if series_name:
            sql += " AND s.seriesTitle LIKE :seriesName"
            params["seriesName"] = f"%{series_name}%"
        
        if season_number:
            sql += " AND e.seNumber = :seNumber"
            params["seNumber"] = int(season_number)
        
        if episode_number:
            sql += " AND e.epNumber = :epNumber"
            params["epNumber"] = int(episode_number)
        
        sql += " LIMIT 100"
        
        # Build display SQL with actual values
        display_sql = sql
        for key, value in params.items():
            if isinstance(value, str):
                display_sql = display_sql.replace(f":{key}", f"'{value}'")
            else:
                display_sql = display_sql.replace(f":{key}", str(value))
        
        result = conn.execute(text(sql), params)
        data = result.fetchall()
    
    title = f"Episodes matching '{ep_title}'" if ep_title else "Episodes"
    return render_template("episodes.html", items=data, title=title, sql_query=display_sql)


@episode_bp.route("/episode/<episode_id>")
def episode_detail(episode_id):
    uid = current_user.id if current_user.is_authenticated else -1
    with engine.connect() as conn:
        # DÜZELTME: 'prof.professionName' yerine alt sorgu eklendi ve 'LEFT JOIN profession' kaldırıldı.
        sql = """
            SELECT 
                e.episodeId, e.epTitle, e.runtimeMinutes, 
                e.seriesId, e.seNumber, e.epNumber,
                s.seriesTitle, s.startYear, s.endYear,
                (SELECT COUNT(DISTINCT e2.seNumber) FROM Episode e2 WHERE e2.seriesId = e.seriesId) AS total_seasons,
                (SELECT COUNT(*) FROM Episode e3 WHERE e3.seriesId = e.seriesId) AS total_episodes,
                g.genreName,
                p.peopleId, p.primaryName, pr.category, pr.characters, 
                (
                    SELECT GROUP_CONCAT(pd.name SEPARATOR ', ') 
                    FROM profession_assignments pa 
                    JOIN profession_dictionary pd ON pa.profession_dict_id = pd.id 
                    WHERE pa.peopleId = p.peopleId
                ) as professionName,
                CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked  
            FROM Episode e
            LEFT JOIN Series s ON e.seriesId = s.seriesId
            LEFT JOIN Series_Genres sg ON s.seriesId = sg.seriesId
            LEFT JOIN genres g ON sg.genreId = g.genreId
            LEFT JOIN principals pr ON pr.titleId = e.seriesId
            LEFT JOIN people p ON pr.peopleId = p.peopleId
            -- LEFT JOIN profession satırı buradan silindi --
            LEFT JOIN githappens_users.user_likes_titles ul ON e.episodeId = ul.title_id AND ul.user_id = :uid
            WHERE e.episodeId = :episodeId
            ORDER BY pr.category, p.primaryName
        """
        
        display_sql = sql.strip().replace(':episodeId', f"'{episode_id}'")
        result = conn.execute(text(sql), {"episodeId": episode_id, "uid": uid})
        rows = result.fetchall()
        
        if not rows:
            flash("Episode not found.")
            return redirect(url_for('episode.episodes'))
        
        # İlk satırdan episode ve stats bilgilerini al
        first_row = rows[0]
        episode = {
            'episodeId': first_row.episodeId,
            'epTitle': first_row.epTitle,
            'runtimeMinutes': first_row.runtimeMinutes,
            'seriesId': first_row.seriesId,
            'seNumber': first_row.seNumber,
            'epNumber': first_row.epNumber,
            'seriesTitle': first_row.seriesTitle,
            'startYear': first_row.startYear,
            'endYear': first_row.endYear,
            'is_liked': first_row.is_liked  
        }
        
        stats = {
            'total_seasons': first_row.total_seasons,
            'total_episodes': first_row.total_episodes
        }
        
        # Unique genres listesi çıkar
        genres = []
        seen_genres = set()
        for row in rows:
            if row.genreName and row.genreName not in seen_genres:
                genres.append(row.genreName)
                seen_genres.add(row.genreName)
        
        # Unique cast listesi çıkar
        cast = []
        seen_people = set()
        for row in rows:
            if row.peopleId and row.peopleId not in seen_people:
                # Corrupted data kontrolü
                characters = row.characters
                if characters and '\n' in characters:
                    characters = characters.split('\n')[0]
                
                cast.append({
                    'peopleId': row.peopleId,
                    'primaryName': row.primaryName,
                    'category': row.category,
                    'characters': characters,
                    'professionName': row.professionName
                })
                seen_people.add(row.peopleId)
    
    return render_template("episode.html", 
                           episode=episode, 
                           genres=genres,
                           stats=stats,
                           cast=cast,
                           sql_query=display_sql)


@episode_bp.route("/characters")
def characters():
    return render_template("characters.html")
