from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
import random
from database.db import engine
from admin import admin_bp   # blueprint buradan geliyor

# ------------------------------------------------------------------
# ADMIN HOME
# ------------------------------------------------------------------
@admin_bp.route("/")
def admin_home():
    return render_template("admin/index.html")

# ------------------------------------------------------------------
# PEOPLE MENU
# ------------------------------------------------------------------
@admin_bp.route("/people/menu")
def person_menu():
    return render_template(
        "admin/manage_generic.html",
        title="People",
        singular="Person",
        add_route="admin.person_new",
        edit_route="admin.person_edit_menu",
        delete_route="admin.person_delete_menu"
    )
    
# ------------------------------------------------------------------
# NEW PERSON
# ------------------------------------------------------------------
@admin_bp.route("/people/new", methods=["GET", "POST"])
def person_new():
    if request.method == "POST":
        name = request.form["primaryName"]
        birth = request.form.get("birthYear")
        death = request.form.get("deathYear")

        # normalize empty strings to NULL
        birth = birth or None
        death = death or None

        with engine.connect() as conn:
            # generate a random peopleId like 'nm0000123' that's not already in DB
            while True:
                candidate_id = f"nm{random.randint(0, 9999999):07d}"
                exists = conn.execute(
                    text("SELECT 1 FROM people WHERE peopleId = :id"),
                    {"id": candidate_id}
                ).fetchone()
                if not exists:
                    break

            conn.execute(
                text("INSERT INTO people (peopleId, primaryName, birthYear, deathYear) VALUES (:id, :n, :b, :d)"),
                {"id": candidate_id, "n": name, "b": birth, "d": death}
            )
            conn.commit()

        flash("New person added!")

    return render_template("person_form.html", person=None)


# ------------------------------------------------------------------
# EDIT PERSON
# ------------------------------------------------------------------
@admin_bp.route("/people/edit/<people_id>", methods=["GET", "POST"])
def person_edit(people_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT peopleId, primaryName, birthYear, deathYear FROM people WHERE peopleId = :id"),
            {"id": people_id}
        )
        person = result.fetchone()

    if request.method == "POST":
        name = request.form["primaryName"]
        birth = request.form.get("birthYear")
        death = request.form.get("deathYear")

        with engine.connect() as conn:
            conn.execute(
                text("UPDATE people SET primaryName=:n, birthYear=:b, deathYear=:d WHERE peopleId=:id"),
                {"n": name, "b": birth, "d": death, "id": people_id}
            )
            conn.commit()

        flash("Person updated!")
        return redirect(url_for("admin.person_edit_menu"))

    return render_template("person_form.html", person=person)


# ------------------------------------------------------------------
# EDIT MENU (Arama sayfası)
# ------------------------------------------------------------------
@admin_bp.route("/people/edit", methods=["GET", "POST"])
def person_edit_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            people = conn.execute(
                text("""
                    SELECT peopleId, primaryName
                    FROM people
                    WHERE primaryName LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            people = conn.execute(
                text("""
                    SELECT peopleId, primaryName
                    FROM people
                    ORDER BY primaryName
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/edit_generic_menu.html",
        title="Person",
        singular="Person",
        items=people,
        id_field="peopleId",
        name_field="primaryName",
        name_label="Name",
        edit_route="admin.person_edit",
        id_param="people_id"
    )


# ------------------------------------------------------------------
# DELETE MENU (Arama sayfası)
# ------------------------------------------------------------------
@admin_bp.route("/people/delete", methods=["GET", "POST"])
def person_delete_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            people = conn.execute(
                text("""
                    SELECT peopleId, primaryName
                    FROM people
                    WHERE primaryName LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            people = conn.execute(
                text("""
                    SELECT peopleId, primaryName
                    FROM people
                    ORDER BY primaryName
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/delete_generic_menu.html",
        title="Person",
        singular="Person",
        items=people,
        id_field="peopleId",
        name_field="primaryName",
        name_label="Name",
        delete_route="admin.person_delete",
        id_param="people_id"
    )

# ------------------------------------------------------------------
# DELETE PERSON
# ------------------------------------------------------------------
@admin_bp.route("/people/delete/<people_id>", methods=["POST"])
def person_delete(people_id):
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM people WHERE peopleId=:id"),
            {"id": people_id}
        )
        conn.commit()

    flash("Person deleted!")
    return redirect(url_for("admin.person_delete_menu"))

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
        movie_id = request.form["movieId"]
        title = request.form["movieTitle"]
        title_type = request.form.get("titleType")
        start_year = request.form.get("startYear")
        runtime = request.form.get("runtimeMinutes")
        is_adult = 1 if request.form.get("isAdult") else 0

        with engine.connect() as conn:
            conn.execute(
                text("""
                    INSERT INTO movies
                    (movieId, movieTitle, titleType, startYear, runtimeMinutes, isAdult)
                    VALUES (:id, :t, :tt, :sy, :rt, :ia)
                """),
                {
                    "id": movie_id,
                    "t": title,
                    "tt": title_type,
                    "sy": start_year or None,
                    "rt": runtime or None,
                    "ia": is_adult
                }
            )
            conn.commit()

        flash("New movie added!")

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
        title_type = request.form.get("titleType")
        start_year = request.form.get("startYear")
        runtime = request.form.get("runtimeMinutes")
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
    with engine.connect() as conn:
        conn.execute(
            text("DELETE FROM movies WHERE movieId = :id"),
            {"id": movie_id}
        )
        conn.commit()

    flash("Movie deleted!")
    return redirect(url_for("admin.movie_delete_menu"))