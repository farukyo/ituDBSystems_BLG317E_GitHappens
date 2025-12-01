# Movie Routes Module
# Handles movie listing and movie detail pages with search and genre filtering.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine

movie_bp = Blueprint('movie', __name__)


@movie_bp.route("/movies")
def movies():
    search_query = request.args.get('q')
    genre_filter = request.args.get('genre')
    
    with engine.connect() as conn:
        sql = "SELECT * FROM movies WHERE 1=1"
        params = {}

        if search_query:
            sql += " AND movieTitle LIKE :q"
            params["q"] = f"%{search_query}%"
        
        if genre_filter:
            sql += " AND genres LIKE :genre"
            params["genre"] = f"%{genre_filter}%"
        
        sql += " LIMIT 100;"
        result = conn.execute(text(sql), params)
        data = result.fetchall()
    
    page_title = f"Results for '{search_query}'" if search_query else "All Movies"
    return render_template("movies.html", items=data, title=page_title)


@movie_bp.route("/movie/<movie_id>")
def movie(movie_id):
    with engine.connect() as conn:
        sql = """
            SELECT movieId, movieTitle, titleType, startYear, runtimeMinutes
            FROM movies
            WHERE movieId = :movieId
        """
        result = conn.execute(text(sql), {"movieId": movie_id})
        movie = result.fetchone()
        
        if not movie:
            flash(f"Movie with ID {movie_id} not found.")
            return redirect(url_for('movie.movies'))
        
        cast_sql = """
            SELECT p.peopleId, p.primaryName, pr.category, pr.characters
            FROM principals pr
            JOIN people p ON pr.peopleId = p.peopleId
            WHERE pr.titleId = :movieId
            ORDER BY pr.category, p.primaryName
        """
        cast_result = conn.execute(text(cast_sql), {"movieId": movie_id})
        cast = cast_result.fetchall()
        
    page_title = f"{movie.movieTitle} ({movie.startYear})"
    return render_template("movie.html", movie=movie, cast=cast, title=page_title)
