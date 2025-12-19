from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp
import random

# ------------------------------------------------------------------
# MOVIES MENU
# ------------------------------------------------------------------
@admin_bp.route("/movies/menu")
def movie_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Movies",
        singular="Movie",
        add_route="admin.movie_new",
        edit_route="admin.movie_edit_menu",
        delete_route="admin.movie_delete_menu"
    )
    
# ------------------------------------------------------------------
# NEW MOVIE
# ------------------------------------------------------------------
@admin_bp.route("/movies/new", methods=["GET", "POST"])
def movie_new():
    if request.method == "POST":
        title = request.form["movieTitle"]
        title_type = request.form.get("titleType")
        start_year = request.form.get("startYear")
        runtime = request.form.get("runtimeMinutes")
        is_adult = 1 if request.form.get("isAdult") else 0

        # Tip dönüşümleri
        start_year = int(start_year) if start_year else None
        runtime = int(runtime) if runtime else None

        with engine.begin() as conn:  # transaction
            # UNIQUE ID üret (PARENT tabloya göre)
            while True:
                candidate_id = f"tt{random.randint(0, 9999999):07d}"
                exists = conn.execute(
                    text("SELECT 1 FROM all_titles WHERE titleId = :id"),
                    {"id": candidate_id}
                ).fetchone()
                if not exists:
                    break

            # 1️⃣ PARENT TABLO
            conn.execute(
                text("""
                    INSERT INTO all_titles (titleId)
                    VALUES (:id)
                """),
                {
                    "id": candidate_id
                }
            )

            # 2️⃣ CHILD TABLO
            conn.execute(
                text("""
                    INSERT INTO movies
                    (movieId, movieTitle, titleType, startYear, runtimeMinutes, isAdult)
                    VALUES (:id, :t, :tt, :sy, :rt, :ia)
                """),
                {
                    "id": candidate_id,
                    "t": title,
                    "tt": title_type,
                    "sy": start_year,
                    "rt": runtime,
                    "ia": is_adult
                }
            )

        flash("New movie added successfully!")

    return render_template("movie_form.html", movie=None)


# ------------------------------------------------------------------
# EDIT MOVIE
# ------------------------------------------------------------------
@admin_bp.route("/movies/edit/<movie_id>", methods=["GET", "POST"])
def movie_edit(movie_id):

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT movieId, movieTitle, titleType,
                       startYear, runtimeMinutes, isAdult
                FROM movies
                WHERE movieId = :id
            """),
            {"id": movie_id}
        )
        movie = result.fetchone()

    if request.method == "POST":
        title = request.form["movieTitle"]
        title_type = request.form.get("titleType") or None
        start_year = request.form.get("startYear") or None
        runtime = request.form.get("runtimeMinutes") or None
        is_adult = 1 if request.form.get("isAdult") else 0

        with engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE movies
                    SET movieTitle = :t,
                        titleType = :tt,
                        startYear = :sy,
                        runtimeMinutes = :rt,
                        isAdult = :ia
                    WHERE movieId = :id
                """),
                {
                    "t": title,
                    "tt": title_type,
                    "sy": start_year or None,
                    "rt": runtime or None,
                    "ia": is_adult,
                    "id": movie_id
                }
            )
            conn.commit()

        flash("Movie updated!")
        return redirect(url_for("admin.movie_edit_menu"))

    return render_template("movie_form.html", movie=movie)


# ------------------------------------------------------------------
# EDIT MOVIE MENU (Search)
# ------------------------------------------------------------------
@admin_bp.route("/movies/edit", methods=["GET", "POST"])
def movie_edit_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            movies = conn.execute(
                text("""
                    SELECT movieId, movieTitle
                    FROM movies
                    WHERE movieTitle LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            movies = conn.execute(
                text("""
                    SELECT movieId, movieTitle
                    FROM movies
                    ORDER BY movieTitle
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/edit_generic_menu.html",
        title="Movie",
        singular="Movie",
        items=movies,
        id_field="movieId",
        name_field="movieTitle",
        name_label="Title",
        edit_route="admin.movie_edit",
        id_param="movie_id"
    )


# ------------------------------------------------------------------
# DELETE MOVIE MENU (Search)
# ------------------------------------------------------------------
@admin_bp.route("/movies/delete", methods=["GET", "POST"])
def movie_delete_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            movies = conn.execute(
                text("""
                    SELECT movieId, movieTitle
                    FROM movies
                    WHERE movieTitle LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            movies = conn.execute(
                text("""
                    SELECT movieId, movieTitle
                    FROM movies
                    ORDER BY movieTitle
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/delete_generic_menu.html",
        title="Movie",
        singular="Movie",
        items=movies,
        id_field="movieId",
        name_field="movieTitle",
        name_label="Title",
        delete_route="admin.movie_delete",
        id_param="movie_id"
    )

# ------------------------------------------------------------------
# DELETE MOVIE
# ------------------------------------------------------------------
@admin_bp.route("/movies/delete/<movie_id>", methods=["POST"])
def movie_delete(movie_id):
    with engine.begin() as conn:
        # 1️⃣ CHILD
        conn.execute(
            text("DELETE FROM movies WHERE movieId = :id"),
            {"id": movie_id}
        )

        # 2️⃣ PARENT
        conn.execute(
            text("DELETE FROM all_titles WHERE titleId = :id"),
            {"id": movie_id}
        )

    flash("Movie deleted successfully!")
    return redirect(url_for("admin.movie_delete_menu"))