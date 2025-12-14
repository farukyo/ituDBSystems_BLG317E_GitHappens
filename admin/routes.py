from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
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
    return render_template("admin/manage_people.html")


# ------------------------------------------------------------------
# NEW PERSON
# ------------------------------------------------------------------
@admin_bp.route("/people/new", methods=["GET", "POST"])
def person_new():
    if request.method == "POST":
        name = request.form["primaryName"]
        birth = request.form.get("birthYear")
        death = request.form.get("deathYear")

        with engine.connect() as conn:
            conn.execute(
                text("INSERT INTO people (primaryName, birthYear, deathYear) VALUES (:n, :b, :d)"),
                {"n": name, "b": birth, "d": death}
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
                text("SELECT peopleId, primaryName FROM people "
                     "WHERE primaryName LIKE :q LIMIT 50"),
                {"q": f"%{query}%"}
            ).fetchall()
        else:
            people = conn.execute(
                text("SELECT peopleId, primaryName FROM people ORDER BY primaryName LIMIT 20")
            ).fetchall()

    return render_template("edit_person_menu.html", people=people)


# ------------------------------------------------------------------
# DELETE MENU (Arama sayfası)
# ------------------------------------------------------------------
@admin_bp.route("/people/delete", methods=["GET", "POST"])
def person_delete_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            people = conn.execute(
                text("SELECT peopleId, primaryName FROM people "
                     "WHERE primaryName LIKE :q LIMIT 50"),
                {"q": f"%{query}%"}
            ).fetchall()
        else:
            people = conn.execute(
                text("SELECT peopleId, primaryName FROM people ORDER BY primaryName LIMIT 20")
            ).fetchall()

    return render_template("delete_person_menu.html", people=people)


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