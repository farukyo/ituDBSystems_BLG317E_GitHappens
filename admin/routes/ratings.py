from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp


# -------------------------------------------------
# TITLE TYPE + NAME → titleId BULMA
# -------------------------------------------------
def get_title_id(conn, title_type, title_name):

    if title_type == "movie":
        row = conn.execute(
            text("SELECT movieId AS id FROM movies WHERE movieTitle = :t"),
            {"t": title_name}
        ).fetchone()

    elif title_type == "series":
        row = conn.execute(
            text("SELECT seriesId AS id FROM Series WHERE seriesTitle = :t"),
            {"t": title_name}
        ).fetchone()

    else:
        return None

    return row.id if row else None


# -------------------------------------------------
# RATINGS MENU
# -------------------------------------------------
@admin_bp.route("/ratings/menu")
def rating_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Ratings",
        singular="Rating",
        add_route="admin.rating_new",
        edit_route="admin.rating_edit_menu",
        delete_route="admin.rating_delete_menu"
    )


# -------------------------------------------------
# NEW RATING
# -------------------------------------------------
@admin_bp.route("/ratings/new", methods=["GET", "POST"])
def rating_new():

    if request.method == "POST":
        title_type = request.form.get("titleType", "").strip()
        title_name = request.form.get("titleName", "").strip()
        avg_rating = request.form.get("averageRating")
        num_votes = request.form.get("numVotes")

        if title_type not in ("movie", "series"):
            flash("Ratings can only be added for movies or series.")
            return redirect(url_for("admin.rating_new"))

        if not title_name:
            flash("Title name is required.")
            return redirect(url_for("admin.rating_new"))

        avg_rating = float(avg_rating) if avg_rating else None
        num_votes = int(num_votes) if num_votes else None

        with engine.begin() as conn:
            title_id = get_title_id(conn, title_type, title_name)

            if not title_id:
                flash("Selected title not found.")
                return redirect(url_for("admin.rating_new"))

            exists = conn.execute(
                text("SELECT 1 FROM ratings WHERE titleId = :id"),
                {"id": title_id}
            ).fetchone()

            if exists:
                flash("This title already has a rating. Use edit instead.")
                return redirect(url_for("admin.rating_new"))

            conn.execute(
                text("""
                    INSERT INTO ratings (titleId, averageRating, numVotes)
                    VALUES (:tid, :avg, :nv)
                """),
                {
                    "tid": title_id,
                    "avg": avg_rating,
                    "nv": num_votes
                }
            )

        flash("New rating added successfully!")
        return redirect(url_for("admin.rating_menu"))

    return render_template("rating_form.html", rating=None)


# -------------------------------------------------
# EDIT RATING
# -------------------------------------------------
@admin_bp.route("/ratings/edit/<int:rating_id>", methods=["GET", "POST"])
def rating_edit(rating_id):

    with engine.connect() as conn:
        rating = conn.execute(
            text("""
                SELECT 
                    r.ratingId,
                    r.averageRating,
                    r.numVotes,
                    COALESCE(
                        m.movieTitle,
                        s.seriesTitle
                    ) AS primaryTitle
                FROM ratings r
                LEFT JOIN movies m ON r.titleId = m.movieId
                LEFT JOIN Series s ON r.titleId = s.seriesId
                WHERE r.ratingId = :id
            """),
            {"id": rating_id}
        ).mappings().fetchone()

    if not rating:
        flash("Rating not found.")
        return redirect(url_for("admin.rating_menu"))

    if request.method == "POST":
        avg_rating = request.form.get("averageRating")
        num_votes = request.form.get("numVotes")

        avg_rating = float(avg_rating) if avg_rating else None
        num_votes = int(num_votes) if num_votes else None

        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE ratings
                    SET averageRating = :avg,
                        numVotes = :nv
                    WHERE ratingId = :id
                """),
                {
                    "avg": avg_rating,
                    "nv": num_votes,
                    "id": rating_id
                }
            )

        flash("Rating updated successfully!")
        return redirect(url_for("admin.rating_menu"))

    return render_template("rating_form.html", rating=rating)


# -------------------------------------------------
# EDIT RATING MENU
# -------------------------------------------------
@admin_bp.route("/ratings/edit", methods=["GET", "POST"])
def rating_edit_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            ratings = conn.execute(
                text("""
                    SELECT 
                        r.ratingId,
                        COALESCE(
                            m.movieTitle,
                            s.seriesTitle
                        ) AS primaryTitle
                    FROM ratings r
                    LEFT JOIN movies m ON r.titleId = m.movieId
                    LEFT JOIN Series s ON r.titleId = s.seriesId
                    WHERE 
                        m.movieTitle LIKE :q OR
                        s.seriesTitle LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            ratings = conn.execute(
                text("""
                    SELECT 
                        r.ratingId,
                        COALESCE(
                            m.movieTitle,
                            s.seriesTitle
                        ) AS primaryTitle
                    FROM ratings r
                    LEFT JOIN movies m ON r.titleId = m.movieId
                    LEFT JOIN Series s ON r.titleId = s.seriesId
                    ORDER BY primaryTitle
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/edit_generic_menu.html",
        title="Ratings",
        singular="Rating",
        items=ratings,
        id_field="ratingId",
        name_field="primaryTitle",
        name_label="Title",
        edit_route="admin.rating_edit",
        id_param="rating_id"
    )


# -------------------------------------------------
# DELETE RATING MENU
# -------------------------------------------------
@admin_bp.route("/ratings/delete", methods=["GET", "POST"])
def rating_delete_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            ratings = conn.execute(
                text("""
                    SELECT 
                        r.ratingId,
                        r.titleId,
                        r.averageRating,
                        r.numVotes,
                        COALESCE(m.movieTitle, s.seriesTitle, e.epTitle) AS primaryTitle
                    FROM ratings r
                    LEFT JOIN movies m ON r.titleId = m.movieId
                    LEFT JOIN Series s ON r.titleId = s.seriesId
                    LEFT JOIN Episode e ON r.titleId = e.episodeId
                    WHERE 
                        m.movieTitle LIKE :q OR
                        s.seriesTitle LIKE :q OR
                        e.epTitle LIKE :q OR
                        r.titleId LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            ratings = conn.execute(
                text("""
                    SELECT 
                        r.ratingId,
                        r.titleId,
                        r.averageRating,
                        r.numVotes,
                        COALESCE(m.movieTitle, s.seriesTitle, e.epTitle) AS primaryTitle
                    FROM ratings r
                    LEFT JOIN movies m ON r.titleId = m.movieId
                    LEFT JOIN Series s ON r.titleId = s.seriesId
                    LEFT JOIN Episode e ON r.titleId = e.episodeId
                    ORDER BY r.ratingId DESC
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/delete_ratings_menu.html",
        title="Ratings",
        singular="Rating",
        items=ratings,
        id_field="ratingId",
        name_field="primaryTitle",
        name_label="Title",
        delete_route="admin.rating_delete",
        id_param="rating_id"
    )


# -------------------------------------------------
# DELETE RATING
# -------------------------------------------------
@admin_bp.route("/ratings/delete/<int:rating_id>", methods=["POST"])
def rating_delete(rating_id):
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM ratings WHERE ratingId = :id"),
            {"id": rating_id}
        )

    flash("Rating deleted successfully!")
    return redirect(url_for("admin.rating_delete_menu"))