# Series Routes Module
# Handles series listing page with search functionality and AJAX support.

from flask import Blueprint, render_template, request
from flask_login import current_user
from sqlalchemy import text
from database.db import engine

series_bp = Blueprint("series", __name__)


@series_bp.route("/series")
def series():
    search_query = request.args.get("q")
    title_type = request.args.get("titleType")
    start_year = request.args.get("startYear")
    end_year = request.args.get("endYear")
    is_adult = request.args.get("isAdult")
    view = request.args.get("view")

    uid = current_user.id if current_user.is_authenticated else -1

    with engine.connect() as conn:
        params = {"uid": uid}

        if view == "stats":
            sql = """
            SELECT 
                s.seriesId,
                s.seriesTitle,
                s.startYear,
                AVG(r.averageRating) AS averageRating,
                COUNT(DISTINCT pr.peopleId) AS cast_count,
                COUNT(DISTINCT g.genreId) AS genre_count,
                GROUP_CONCAT(DISTINCT g.genreName SEPARATOR ', ') AS genre_str,
                CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
            FROM series s
            LEFT JOIN ratings r ON s.seriesId = r.titleId
            LEFT JOIN principals pr ON s.seriesId = pr.titleId
            LEFT JOIN Series_Genres sg ON s.seriesId = sg.seriesId
            LEFT JOIN genres g ON sg.genreId = g.genreId
            LEFT JOIN githappens_users.user_likes_titles ul ON s.seriesId = ul.title_id AND ul.user_id = :uid
            WHERE 1=1
            """

            if search_query:
                sql += " AND seriesTitle LIKE :q"
                params["q"] = f"%{search_query}%"

            if title_type:
                sql += " AND titleType = :tType"
                params["tType"] = title_type

            if start_year and start_year.isdigit():
                sql += " AND startYear = :sYear"
                params["sYear"] = int(start_year)

            if end_year and end_year.isdigit():
                sql += " AND (endYear IS NULL OR endYear <= :eYear)"
                params["eYear"] = int(end_year)

            if is_adult is not None and is_adult != "":
                sql += " AND isAdult = :adult"
                params["adult"] = int(is_adult)

            sql += """
            GROUP BY 
                s.seriesId, s.seriesTitle, s.startYear, r.averageRating
            ORDER BY r.averageRating DESC
            LIMIT 100
            """

        else:
            sql = """
            SELECT 
                s.seriesId,
                s.seriesTitle,
                s.titleType,
                s.startYear,
                s.endYear,
                s.runtimeMinutes,
                s.isAdult,
                AVG(r.averageRating) AS averageRating,
                SUM(r.numVotes) AS numVotes,
                GROUP_CONCAT(DISTINCT g.genreName SEPARATOR ', ') AS genre_str,
                CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END AS is_liked
            FROM series s
            LEFT JOIN ratings r 
                   ON s.seriesId = r.titleId
            LEFT JOIN Series_Genres sg 
                   ON s.seriesId = sg.seriesId
            LEFT JOIN genres g 
                   ON sg.genreId = g.genreId
            LEFT JOIN githappens_users.user_likes_titles ul 
                   ON s.seriesId = ul.title_id AND ul.user_id = :uid
            WHERE 1=1
            """

            if search_query:
                sql += " AND seriesTitle LIKE :q"
                params["q"] = f"%{search_query}%"

            if title_type:
                sql += " AND titleType = :tType"
                params["tType"] = title_type

            if start_year and start_year.isdigit():
                sql += " AND startYear = :sYear"
                params["sYear"] = int(start_year)

            if end_year and end_year.isdigit():
                sql += " AND (endYear IS NULL OR endYear <= :eYear)"
                params["eYear"] = int(end_year)

            if is_adult is not None and is_adult != "":
                sql += " AND isAdult = :adult"
                params["adult"] = int(is_adult)

            sql += """
            AND s.seriesId IN (
                SELECT r2.titleId
                FROM ratings r2
                GROUP BY r2.titleId
                HAVING AVG(r2.averageRating) >= 7
            )
            """

            sql += """
            GROUP BY
                s.seriesId,
                s.seriesTitle,
                s.titleType,
                s.startYear,
                s.endYear,
                s.runtimeMinutes,
                s.isAdult,
                ul.user_id
            """

            sql += " ORDER BY numVotes DESC, seriesTitle ASC LIMIT 100;"

        result = conn.execute(text(sql), params)
        data = result.fetchall()

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

    if view == "stats":
        page_title = "Detailed Series Statistics"
    elif search_query:
        page_title = f"Results for '{search_query}'"
    else:
        page_title = "Series Results"

    return render_template("series.html", items=data, title=page_title)


@series_bp.route("/series/<series_id>")
def serie_detail(series_id):
    uid = current_user.id if current_user.is_authenticated else -1
    with engine.connect() as conn:
        sql_series = """
            SELECT s.seriesId, s.seriesTitle, s.titleType, s.startYear, s.endYear, s.runtimeMinutes, s.isAdult,
                   CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
            FROM series s
            LEFT JOIN githappens_users.user_likes_titles ul ON s.seriesId = ul.title_id AND ul.user_id = :uid
            WHERE s.seriesId = :id
        """
        series = conn.execute(
            text(sql_series), {"id": series_id, "uid": uid}
        ).fetchone()

        if not series:
            from flask import flash, redirect, url_for

            flash("Series not found.")
            return redirect(url_for("series.series"))

        sql_genres = """
            SELECT g.genreName
            FROM Series_Genres sg
            JOIN genres g ON sg.genreId = g.genreId
            WHERE sg.seriesId = :id
        """
        genres = [
            r.genreName
            for r in conn.execute(text(sql_genres), {"id": series_id}).fetchall()
        ]

        sql_cast = """
            SELECT p.peopleId, p.primaryName, pr.category, pr.characters
            FROM principals pr
            JOIN people p ON pr.peopleId = p.peopleId
            WHERE pr.titleId = :id 
            AND pr.category IN ('actor', 'actress', 'self')
            LIMIT 20
        """
        cast_data = conn.execute(text(sql_cast), {"id": series_id}).fetchall()

        cast = []
        for person in cast_data:
            chars = person.characters
            if chars and isinstance(chars, str):
                if "\n" in chars or "\r" in chars:
                    chars = chars.splitlines()[0]

                if chars.startswith("["):
                    import json

                    try:
                        parsed = json.loads(chars)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            chars = parsed[0]
                    except Exception:
                        pass

                chars = chars.strip('"')
            else:
                chars = None

            cast.append(
                {
                    "peopleId": person.peopleId,
                    "primaryName": person.primaryName,
                    "category": person.category,
                    "characters": chars,
                }
            )

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
                "total_episodes": stats_result.total_episodes if stats_result else 0,
            }
        except Exception:
            stats = {"total_seasons": 0, "total_episodes": 0}

        sql_rating = """
            SELECT averageRating, numVotes
            FROM ratings
            WHERE titleId = :id
        """
        rating_result = conn.execute(text(sql_rating), {"id": series_id}).fetchone()
        rating = {
            "rating": rating_result.averageRating if rating_result else 0,
            "votes": rating_result.numVotes if rating_result else 0,
        }

    page_title = f"{series.seriesTitle} ({series.startYear})"
    return render_template(
        "serie.html",
        series=series,
        genres=genres,
        cast=cast,
        stats=stats,
        rating=rating,
        title=page_title,
    )
