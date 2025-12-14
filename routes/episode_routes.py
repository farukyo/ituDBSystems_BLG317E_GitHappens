# Episode Routes Module
# Handles episode listing and detail pages with advanced filtering options.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
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
    
    with engine.connect() as conn:
        sql = """
            SELECT e.episodeId, e.epTitle, e.runtimeMinutes, 
                   e.seriesId, e.seNumber, e.epNumber,
                   s.seriesTitle
            FROM Episode e
            LEFT JOIN Series s ON e.seriesId = s.seriesId
            WHERE 1=1
        """
        params = {}
        
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
    with engine.connect() as conn:
        sql = """
            SELECT e.episodeId, e.epTitle, e.runtimeMinutes, 
                   e.seriesId, e.seNumber, e.epNumber,
                   s.seriesTitle, s.startYear, s.endYear
            FROM Episode e
            LEFT JOIN Series s ON e.seriesId = s.seriesId
            WHERE e.episodeId = :episodeId
        """
        result = conn.execute(text(sql), {"episodeId": episode_id})
        episode = result.fetchone()
        
        if not episode:
            flash("Episode not found.")
            return redirect(url_for('episode.episodes'))
        
        genres_sql = """
            SELECT g.genreName
            FROM Series_Genres sg
            JOIN genres g ON sg.genreId = g.genreId
            WHERE sg.seriesId = :seriesId
        """
        genres_result = conn.execute(text(genres_sql), {"seriesId": episode.seriesId})
        genres = [row.genreName for row in genres_result.fetchall()]
        
        stats_sql = """
            SELECT 
                COUNT(DISTINCT seNumber) as total_seasons,
                COUNT(*) as total_episodes
            FROM Episode
            WHERE seriesId = :seriesId
        """
        stats_result = conn.execute(text(stats_sql), {"seriesId": episode.seriesId})
        stats = stats_result.fetchone()
        
        cast_sql = """
            SELECT p.peopleId, p.primaryName, pr.category, pr.characters,
                   prof.professionName
            FROM principals pr
            JOIN people p ON pr.peopleId = p.peopleId
            LEFT JOIN profession prof ON p.professionId = prof.professionId
            WHERE pr.titleId = :seriesId
            ORDER BY pr.category
        """
        cast_result = conn.execute(text(cast_sql), {"seriesId": episode.seriesId})
        raw_cast = cast_result.fetchall()
        
        # Workaround for corrupted data: parse embedded CSV rows from characters field
        cast = []
        if raw_cast:
            first_row = raw_cast[0]
            if first_row.characters and '\n' in first_row.characters:
                # Data is corrupted - parse embedded CSV
                import re
                lines = first_row.characters.replace('\r\n', '\n').split('\n')
                
                # First entry is the actual first character
                first_char = lines[0] if lines else None
                cast.append({
                    'peopleId': first_row.peopleId,
                    'primaryName': first_row.primaryName,
                    'category': first_row.category,
                    'characters': first_char,
                    'professionName': first_row.professionName
                })
                
                # Parse remaining lines as CSV rows for the same series
                series_id = episode.seriesId
                for line in lines[1:]:
                    if line.startswith(series_id + ','):
                        # Parse CSV: titleId,ordering,peopleId,category,job,characters
                        parts = line.split(',', 5)
                        if len(parts) >= 6:
                            char_value = parts[5].strip('"').replace('["', '').replace('"]', '')
                            # Get person name from database
                            person_sql = text("SELECT primaryName FROM people WHERE peopleId = :pid")
                            person_result = conn.execute(person_sql, {"pid": parts[2]})
                            person = person_result.fetchone()
                            if person:
                                cast.append({
                                    'peopleId': parts[2],
                                    'primaryName': person.primaryName,
                                    'category': parts[3],
                                    'characters': char_value if char_value != '0' else None,
                                    'professionName': None
                                })
            else:
                # Data is not corrupted, use as-is
                for row in raw_cast:
                    cast.append({
                        'peopleId': row.peopleId,
                        'primaryName': row.primaryName,
                        'category': row.category,
                        'characters': row.characters,
                        'professionName': row.professionName
                    })
    
    return render_template("episode.html", 
                           episode=episode, 
                           genres=genres,
                           stats=stats,
                           cast=cast)


@episode_bp.route("/characters")
def characters():
    return render_template("characters.html")
