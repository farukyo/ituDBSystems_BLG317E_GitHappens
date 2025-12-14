# Movie Routes Module
# Handles movie listing and movie detail pages with search and genre filtering.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine

movie_bp = Blueprint('movie', __name__)


@movie_bp.route("/movies")
def movies():
    title_query = request.args.get('title')
    genre_filter = request.args.get('genre')
    year_filter = request.args.get('year')
    min_rating = request.args.get('min_rating')
    max_rating = request.args.get('max_rating')
    
    with engine.connect() as conn:
      
        genre_sql = """
            SELECT DISTINCT g.genreName 
            FROM genres g
            JOIN movie_genres mg ON g.genreId = mg.genreId
            ORDER BY g.genreName ASC
        """
        genre_result = conn.execute(text(genre_sql))
        genres_list = [row[0] for row in genre_result.fetchall()]
        
        sql = """
            SELECT m.*, 
                   r.averageRating, 
                   r.numVotes,      
            (
                SELECT GROUP_CONCAT(g.genreName SEPARATOR ', ')
                FROM movie_genres mg
                JOIN genres g ON mg.genreId = g.genreId
                WHERE mg.movieId = m.movieId
            ) as genre_str
            FROM movies m 
            LEFT JOIN ratings r ON m.movieId = r.titleId
            WHERE 1=1
        """
        params = {}
        
        # Title Filtresi 
        if title_query:
            sql += " AND m.movieTitle LIKE :title"
            params["title"] = f"%{title_query}%"
        
        # Genre Filtresi 
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

        # Yıl Filtresi (AYNI KALACAK)
        if year_filter:
            sql += " AND startYear = :year"
            params["year"] = year_filter

        # Puan Filtresi (Min - Max) - R.averageRating kullanılıyor
        if min_rating:
            # SADECE ratings tablosunda puanı olanlar için filtreleme
            sql += " AND r.averageRating >= :min_rating"
            params["min_rating"] = min_rating
            
        if max_rating:
            sql += " AND r.averageRating <= :max_rating"
            params["max_rating"] = max_rating

        # Sıralama ve Limit
        # Puanı yüksek olanları önce göstermek için sıralama ekleyelim
        sql += " ORDER BY r.averageRating DESC, m.movieTitle ASC" # Puanı yüksek olanlar öne gelsin
        sql += " LIMIT 100;"
        
        result = conn.execute(text(sql), params)
        data = result.fetchall()

    # Title
    if title_query:
        page_title = f"Results for '{title_query}'"
    elif genre_filter:
        page_title = f"{genre_filter} Movies"
    else:
        page_title = "All Movies"
    
    return render_template("movies.html", movies=data, genres=genres_list, title=page_title)




@movie_bp.route("/movie/<movie_id>")
def movie(movie_id):
    with engine.connect() as conn:
        sql = """
            SELECT m.*, r.averageRating, r.numVotes
            FROM movies m
            LEFT JOIN ratings r ON m.movieId = r.titleId  -- ratings tablosunu bağla
            WHERE m.movieId = :movieId
        """
        result = conn.execute(text(sql), {"movieId": movie_id})
        movie = result.fetchone()
        
        if not movie:
            flash(f"Movie with ID {movie_id} not found.")
            return redirect(url_for('movie.movies'))
        # Film Detay sayfasında (movie.html) kullanıldığı için türleri çekelim:
        genre_sql = """
            SELECT g.genreName 
            FROM movie_genres mg
            JOIN genres g ON mg.genreId = g.genreId
            WHERE mg.movieId = :movieId
        """
        genre_result = conn.execute(text(genre_sql), {"movieId": movie_id})
        genres = [row[0] for row in genre_result.fetchall()]
        
        # Rating bilgilerini stats dict'ine toplayıp template'e gönderelim
        stats = {
            'averageRating': movie.averageRating,
            'numVotes': movie.numVotes
        }
        
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
    return render_template("movie.html", movie=movie, cast=cast, genres=genres, stats=stats, title=page_title)