from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp


# ==========================================================
# GENRES MENU
# ==========================================================
@admin_bp.route("/genres/menu")
def genre_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Genres",
        singular="Genre",
        add_route="admin.genre_new",
        edit_route="admin.genre_edit_menu",
        delete_route="admin.genre_delete_menu",
        extra_route="admin.genre_assign",
        extra_label="Assign Genres",
    )


# ==========================================================
# NEW GENRE
# ==========================================================
@admin_bp.route("/genres/new", methods=["GET", "POST"])
def genre_new():
    if request.method == "POST":
        genre_id = request.form.get("genreId")
        genre_name = request.form.get("genreName", "").strip()
        description = request.form.get("description")

        if not genre_id or not genre_name:
            flash("Genre ID and Genre Name are required.")
            return redirect(url_for("admin.genre_new"))

        with engine.begin() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM genres WHERE genreId = :id"), {"id": genre_id}
            ).fetchone()

            if exists:
                flash("This genre ID already exists.")
                return redirect(url_for("admin.genre_new"))

            conn.execute(
                text("""
                    INSERT INTO genres (genreId, genreName, description)
                    VALUES (:id, :name, :desc)
                """),
                {"id": genre_id, "name": genre_name, "desc": description},
            )

        flash("Genre added successfully!")
        return redirect(url_for("admin.genre_menu"))

    return render_template("genre_form.html", genre=None)


# ==========================================================
# EDIT GENRE
# ==========================================================
@admin_bp.route("/genres/edit/<int:genre_id>", methods=["GET", "POST"])
def genre_edit(genre_id):
    with engine.connect() as conn:
        genre = (
            conn.execute(
                text("""
                SELECT genreId, genreName, description
                FROM genres
                WHERE genreId = :id
            """),
                {"id": genre_id},
            )
            .mappings()
            .fetchone()
        )

    if not genre:
        flash("Genre not found.")
        return redirect(url_for("admin.genre_menu"))

    if request.method == "POST":
        new_name = request.form.get("genreName", "").strip()
        description = request.form.get("description")

        if not new_name:
            flash("Genre name cannot be empty.")
            return redirect(url_for("admin.genre_edit", genre_id=genre_id))

        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE genres
                    SET genreName = :name,
                        description = :desc
                    WHERE genreId = :id
                """),
                {"name": new_name, "desc": description, "id": genre_id},
            )

        flash("Genre updated successfully!")
        return redirect(url_for("admin.genre_menu"))

    return render_template("genre_form.html", genre=genre)


# ==========================================================
# EDIT GENRE MENU
# ==========================================================
@admin_bp.route("/genres/edit", methods=["GET", "POST"])
def genre_edit_menu():
    query = request.form.get("search", "")

    with engine.connect() as conn:
        genres = (
            conn.execute(
                text("""
                SELECT genreId, genreName
                FROM genres
                WHERE genreName LIKE :q
                ORDER BY genreName
                LIMIT 50
            """),
                {"q": f"%{query}%"},
            )
            .mappings()
            .all()
        )

    return render_template(
        "admin/edit_generic_menu.html",
        title="Genres",
        singular="Genre",
        items=genres,
        id_field="genreId",
        name_field="genreName",
        name_label="Genre Name",
        edit_route="admin.genre_edit",
        id_param="genre_id",
    )


# ==========================================================
# DELETE GENRE MENU
# ==========================================================
@admin_bp.route("/genres/delete", methods=["GET", "POST"])
def genre_delete_menu():
    query = request.form.get("search", "")

    with engine.connect() as conn:
        genres = (
            conn.execute(
                text("""
                SELECT genreId, genreName
                FROM genres
                WHERE genreName LIKE :q
                ORDER BY genreName
                LIMIT 50
            """),
                {"q": f"%{query}%"},
            )
            .mappings()
            .all()
        )

    return render_template(
        "admin/delete_generic_menu.html",
        title="Genres",
        singular="Genre",
        items=genres,
        id_field="genreId",
        name_field="genreName",
        name_label="Genre Name",
        delete_route="admin.genre_delete",
        id_param="genre_id",
    )


# ==========================================================
# DELETE GENRE (FK CHECK)
# ==========================================================
@admin_bp.route("/genres/delete/<int:genre_id>", methods=["POST"])
def genre_delete(genre_id):
    with engine.begin() as conn:
        used_in_movies = conn.execute(
            text("SELECT 1 FROM Movie_Genres WHERE genreId = :id"), {"id": genre_id}
        ).fetchone()

        used_in_series = conn.execute(
            text("SELECT 1 FROM Series_Genres WHERE genreId = :id"), {"id": genre_id}
        ).fetchone()

        if used_in_movies or used_in_series:
            flash("This genre is used by movies or series and cannot be deleted.")
            return redirect(url_for("admin.genre_delete_menu"))

        conn.execute(text("DELETE FROM genres WHERE genreId = :id"), {"id": genre_id})

    flash("Genre deleted successfully!")
    return redirect(url_for("admin.genre_delete_menu"))


# ==========================================================
# ASSIGN GENRES (MOVIE / SERIES)
# ==========================================================
@admin_bp.route("/genres/assign", methods=["GET", "POST"])
def genre_assign():
    with engine.connect() as conn:
        genres = (
            conn.execute(
                text("SELECT genreId, genreName FROM genres ORDER BY genreName")
            )
            .mappings()
            .all()
        )

    if request.method == "POST":
        title_type = request.form.get("titleType")
        title_name = request.form.get("titleName", "").strip()
        genre_ids = request.form.getlist("genreIds")

        if not title_type or not title_name or not genre_ids:
            flash("All fields are required.")
            return redirect(url_for("admin.genre_assign"))

        with engine.begin() as conn:
            if title_type == "movie":
                row = conn.execute(
                    text("SELECT movieId FROM movies WHERE movieTitle = :t"),
                    {"t": title_name},
                ).fetchone()
                table = "Movie_Genres"
                col = "movieId"

            else:
                row = conn.execute(
                    text("SELECT seriesId FROM Series WHERE seriesTitle = :t"),
                    {"t": title_name},
                ).fetchone()
                table = "Series_Genres"
                col = "seriesId"

            if not row:
                flash("Title not found.")
                return redirect(url_for("admin.genre_assign"))

            title_id = row[0]

            # önce eski ilişkileri sil
            conn.execute(
                text(f"DELETE FROM {table} WHERE {col} = :id"), {"id": title_id}
            )

            # yenileri ekle
            for gid in genre_ids:
                conn.execute(
                    text(f"""
                        INSERT INTO {table} ({col}, genreId)
                        VALUES (:tid, :gid)
                    """),
                    {"tid": title_id, "gid": gid},
                )

        flash("Genres assigned successfully!")
        return redirect(url_for("admin.genre_menu"))

    return render_template("admin/genre_assign.html", genres=genres)
