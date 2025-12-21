# Series Routes Module
# Handles series listing page with search functionality and AJAX support.

from flask import Blueprint, render_template, request
from sqlalchemy import text
from database.db import engine

series_bp = Blueprint('series', __name__)


@series_bp.route("/series")
def series():
    # 1. URL Parametrelerini Al
    search_query = request.args.get('q')
    title_type = request.args.get('titleType')
    start_year = request.args.get('startYear')
    end_year = request.args.get('endYear')
    is_adult = request.args.get('isAdult')

    with engine.connect() as conn:
        # 2. Temel Sorgu
        sql = """
            SELECT s.seriesId, s.seriesTitle, s.titleType, s.startYear, s.endYear, s.runtimeMinutes, s.isAdult,
                   r.averageRating, r.numVotes,
                   (
                       SELECT GROUP_CONCAT(g.genreName SEPARATOR ', ')
                       FROM Series_Genres sg
                       JOIN genres g ON sg.genreId = g.genreId
                       WHERE sg.seriesId = s.seriesId
                   ) as genre_str
            FROM series s
            LEFT JOIN ratings r ON s.seriesId = r.titleId
            WHERE 1=1
        """
        params = {}

        # 3. Filtreleme Mantığı
        
        # -- Title Search --
        if search_query:
            sql += " AND seriesTitle LIKE :q"
            params["q"] = f"%{search_query}%"
        
        # -- Title Type --
        if title_type:
            sql += " AND titleType = :tType"
            params["tType"] = title_type

        # -- Start Year --
        if start_year and start_year.isdigit():
            sql += " AND startYear = :sYear"
            params["sYear"] = int(start_year)

        # -- End Year --
        # DİKKAT: Verilerinde endYear genelde NULL. 
        # endYear filtresi seçildiğinde: NULL olanlar (devam edenler) + o yıla kadar bitenler
        if end_year and end_year.isdigit():
            sql += " AND (endYear IS NULL OR endYear <= :eYear)"
            params["eYear"] = int(end_year)

        # -- Adult Content --
        if is_adult is not None and is_adult != "":
            sql += " AND isAdult = :adult"
            params["adult"] = int(is_adult)

        # 4. Sıralama ve Limit
        sql += " ORDER BY r.numVotes DESC, seriesTitle ASC LIMIT 100;"

        result = conn.execute(text(sql), params)
        data = result.fetchall()

    # AJAX request check
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        html_snippets = ""
        for row in data:
            html_snippets += f"""
            <div class="series-card">
                <h3>{row.seriesTitle}</h3>
                <p class="series-genre">N/A</p>
                <p class="series-likes">Liked by 0 users</p>
            </div>
            """
        return html_snippets

    page_title = f"Results for '{search_query}'" if search_query else "Series Results"
    return render_template("series.html", items=data, title=page_title)


@series_bp.route("/series/<series_id>")
def serie_detail(series_id):
    with engine.connect() as conn:
        # 1. Dizi Temel Bilgileri
        sql_series = """
            SELECT seriesId, seriesTitle, titleType, startYear, endYear, runtimeMinutes, isAdult
            FROM series
            WHERE seriesId = :id
        """
        series = conn.execute(text(sql_series), {"id": series_id}).fetchone()

        if not series:
            from flask import flash, redirect, url_for
            flash("Series not found.")
            return redirect(url_for('series.series'))

        # 2. Türler (Genres)
        sql_genres = """
            SELECT g.genreName
            FROM Series_Genres sg
            JOIN genres g ON sg.genreId = g.genreId
            WHERE sg.seriesId = :id
        """
        genres = [r.genreName for r in conn.execute(text(sql_genres), {"id": series_id}).fetchall()]

        # 3. Oyuncular (Cast) - Sadece acting categories
        sql_cast = """
            SELECT p.peopleId, p.primaryName, pr.category, pr.characters
            FROM principals pr
            JOIN people p ON pr.peopleId = p.peopleId
            WHERE pr.titleId = :id 
            AND pr.category IN ('actor', 'actress', 'self')
            LIMIT 20
        """
        cast_data = conn.execute(text(sql_cast), {"id": series_id}).fetchall()
        
        # Characters JSON'ı parse et
        import json
        cast = []
        for person in cast_data:
            try:
                # characters string'i parse et - JSON array veya single string olabilir
                chars = person.characters
                if chars and chars != '\\N':
                    if isinstance(chars, str):
                        # JSON array ise
                        if chars.startswith('['):
                            chars = json.loads(chars)[0] if json.loads(chars) else ''
                        # Tırnak işaretlerini temizle
                        chars = chars.strip('"')
                else:
                    chars = None
            except:
                chars = None
            
            cast.append({
                'peopleId': person.peopleId,
                'primaryName': person.primaryName,
                'category': person.category,
                'characters': chars
            })


        # 4. İstatistikler (Seasons ve Episodes)
        try:
            sql_stats = """
                SELECT COUNT(DISTINCT seNumber) as total_seasons,
                       COUNT(*) as total_episodes
                FROM Episode
                WHERE seriesId = :id
            """
            stats_result = conn.execute(text(sql_stats), {"id": series_id}).fetchone()
            stats = {
                "total_seasons": stats_result.total_seasons if stats_result else 0,
                "total_episodes": stats_result.total_episodes if stats_result else 0
            }
        except:
            # Episode tablosu yoksa default değer
            stats = {
                "total_seasons": 0,
                "total_episodes": 0
            }

        # 5. Rating ve Votes
        sql_rating = """
            SELECT averageRating, numVotes
            FROM ratings
            WHERE titleId = :id
        """
        rating_result = conn.execute(text(sql_rating), {"id": series_id}).fetchone()
        rating = {
            "rating": rating_result.averageRating if rating_result else 0,
            "votes": rating_result.numVotes if rating_result else 0
        }

    page_title = f"{series.seriesTitle} ({series.startYear})"
    return render_template("serie.html", 
                           series=series, 
                           genres=genres,
                           cast=cast,
                           stats=stats,
                           rating=rating,
                           title=page_title)
