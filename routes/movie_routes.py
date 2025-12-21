# Movie Routes Module
# Handles movie listing and movie detail pages with search and genre filtering.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from flask_login import current_user
from database.db import engine

movie_bp = Blueprint('movie', __name__)


@movie_bp.route("/movies")
def movies():
    title_query = request.args.get('title')
    genre_filter = request.args.get('genre')
    year_filter = request.args.get('year')
    min_rating = request.args.get('min_rating')
    max_rating = request.args.get('max_rating')
    view = request.args.get('view')

    uid = current_user.id if current_user.is_authenticated else -1
    with engine.connect() as conn:

        
        genre_sql = """
            SELECT DISTINCT g.genreName 
            FROM genres g
            JOIN movie_genres mg ON g.genreId = mg.genreId
            ORDER BY g.genreName ASC
        """
        genres_list = [row[0] for row in conn.execute(text(genre_sql)).fetchall()]

        params = {"uid": uid}

        if view == "stats":
            sql = """
            SELECT 
                m.movieId,
                m.movieTitle,
                m.startYear,
                r.averageRating,
                COUNT(DISTINCT pr.peopleId) AS cast_count,
                COUNT(DISTINCT g.genreId) AS genre_count,
                GROUP_CONCAT(DISTINCT g.genreName SEPARATOR ', ') AS genre_str,
                CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
            FROM movies m
            LEFT JOIN ratings r ON m.movieId = r.titleId
            LEFT JOIN principals pr ON m.movieId = pr.titleId
            LEFT JOIN movie_genres mg ON m.movieId = mg.movieId
            LEFT JOIN genres g ON mg.genreId = g.genreId
            LEFT JOIN githappens_users.user_likes_titles ul ON m.movieId = ul.title_id AND ul.user_id = :uid
            WHERE 1=1
            """

            if title_query:
                sql += " AND m.movieTitle LIKE :title"
                params["title"] = f"%{title_query}%"

            if genre_filter:
                sql += " AND g.genreName = :genre"
                params["genre"] = genre_filter

            if year_filter:
                sql += " AND m.startYear = :year"
                params["year"] = year_filter

            if min_rating:
                sql += " AND r.averageRating >= :min_rating"
                params["min_rating"] = min_rating

            if max_rating:
                sql += " AND r.averageRating <= :max_rating"
                params["max_rating"] = max_rating

            sql += """
            GROUP BY 
                m.movieId, m.movieTitle, m.startYear, r.averageRating
            ORDER BY r.averageRating DESC
            LIMIT 100
            """

        else:
            sql = """
            SELECT m.*, 
                r.averageRating, 
                r.numVotes,
                (
                    SELECT GROUP_CONCAT(g.genreName SEPARATOR ', ')
                    FROM movie_genres mg
                    JOIN genres g ON mg.genreId = g.genreId
                    WHERE mg.movieId = m.movieId
                ) as genre_str,
                CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
            FROM movies m 
            LEFT JOIN ratings r ON m.movieId = r.titleId
            LEFT JOIN githappens_users.user_likes_titles ul ON m.movieId = ul.title_id AND ul.user_id = :uid
            WHERE 1=1
            """

            if title_query:
                sql += " AND m.movieTitle LIKE :title"
                params["title"] = f"%{title_query}%"

            if genre_filter:
                sql += """
                AND m.movieId IN (
                    SELECT mg.movieId
                    FROM movie_genres mg
                    JOIN genres g ON mg.genreId = g.genreId
                    WHERE g.genreName = :genre
                )
                """
                params["genre"] = genre_filter

            if year_filter:
                sql += " AND m.startYear = :year"
                params["year"] = year_filter

            if min_rating:
                sql += " AND r.averageRating >= :min_rating"
                params["min_rating"] = min_rating

            if max_rating:
                sql += " AND r.averageRating <= :max_rating"
                params["max_rating"] = max_rating

            sql += " ORDER BY r.numVotes DESC, m.movieTitle ASC LIMIT 100"

        data = conn.execute(text(sql), params).fetchall()

    
    if view == "stats":
        page_title = "Detailed Movie Statistics"
    elif title_query:
        page_title = f"Results for '{title_query}'"
    elif genre_filter:
        page_title = f"{genre_filter} Movies"
    else:
        page_title = "All Movies"

    return render_template(
        "movies.html",
        movies=data,
        genres=genres_list,
        title=page_title
    )





@movie_bp.route("/movie/<movie_id>")
def movie(movie_id):
    uid = current_user.id if current_user.is_authenticated else -1
    
    with engine.connect() as conn:
        sql = """
            SELECT m.*, r.averageRating, r.numVotes,
                   CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked  
            FROM movies m
            LEFT JOIN ratings r ON m.movieId = r.titleId
            LEFT JOIN githappens_users.user_likes_titles ul ON m.movieId = ul.title_id AND ul.user_id = :uid
            WHERE m.movieId = :movieId
        """
        result = conn.execute(text(sql), {"movieId": movie_id, "uid": uid})
        movie = result.fetchone()
        
        if not movie:
            flash(f"Movie with ID {movie_id} not found.")
            return redirect(url_for('movie.movies'))
        
        genre_sql = """
            SELECT g.genreName 
            FROM movie_genres mg
            JOIN genres g ON mg.genreId = g.genreId
            WHERE mg.movieId = :movieId
        """
        genre_result = conn.execute(text(genre_sql), {"movieId": movie_id})
        genres = [row[0] for row in genre_result.fetchall()]
        
        
        stats = {
            'averageRating': movie.averageRating,
            'numVotes': movie.numVotes
        }
        
        cast_sql = text("""
            SELECT p.peopleId, p.primaryName, pr.category, pr.characters
            FROM principals pr
            JOIN people p ON pr.peopleId = p.peopleId
            WHERE pr.titleId = :id OR pr.titleId LIKE :like_id
        """)
        
        like_param = f"%{movie_id}" if not str(movie_id).startswith('tt') else movie_id
        cast_result = conn.execute(cast_sql, {"id": movie_id, "like_id": like_param}).fetchall()
        
        
        cast = []
        for row in cast_result:
            d = dict(row._mapping)
            chars = d.get('characters')
            if chars and isinstance(chars, str):
                
                if '\n' in chars or '\r' in chars:
                    chars = chars.splitlines()[0]
                
                
                if chars.startswith('['):
                    import json
                    try:
                        parsed = json.loads(chars)
                        if isinstance(parsed, list) and len(parsed) > 0:
                            chars = parsed[0]
                    except:
                        pass
                
                d['characters'] = chars.strip('"')
            cast.append(d)


    page_title = f"{movie.movieTitle} ({movie.startYear})"
    return render_template("movie.html", movie=movie, cast=cast, genres=genres, stats=stats, title=page_title)