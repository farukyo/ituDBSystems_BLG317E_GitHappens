from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp
import random


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
        delete_route="admin.person_delete_menu",
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
                    {"id": candidate_id},
                ).fetchone()
                if not exists:
                    break

            conn.execute(
                text(
                    "INSERT INTO people (peopleId, primaryName, birthYear, deathYear) VALUES (:id, :n, :b, :d)"
                ),
                {"id": candidate_id, "n": name, "b": birth, "d": death},
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
            text(
                "SELECT peopleId, primaryName, birthYear, deathYear FROM people WHERE peopleId = :id"
            ),
            {"id": people_id},
        )
        person = result.fetchone()

    if request.method == "POST":
        name = request.form["primaryName"]
        birth = request.form.get("birthYear") or None
        death = request.form.get("deathYear") or None

        with engine.connect() as conn:
            conn.execute(
                text(
                    "UPDATE people SET primaryName=:n, birthYear=:b, deathYear=:d WHERE peopleId=:id"
                ),
                {"n": name, "b": birth, "d": death, "id": people_id},
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
            people = (
                conn.execute(
                    text("""
                    SELECT peopleId, primaryName
                    FROM people
                    WHERE primaryName LIKE :q
                    LIMIT 50
                """),
                    {"q": f"%{query}%"},
                )
                .mappings()
                .all()
            )
        else:
            people = (
                conn.execute(
                    text("""
                    SELECT peopleId, primaryName
                    FROM people
                    ORDER BY primaryName
                    LIMIT 20
                """)
                )
                .mappings()
                .all()
            )

    return render_template(
        "admin/edit_generic_menu.html",
        title="Person",
        singular="Person",
        items=people,
        id_field="peopleId",
        name_field="primaryName",
        name_label="Name",
        edit_route="admin.person_edit",
        id_param="people_id",
    )


# ------------------------------------------------------------------
# DELETE MENU (Arama sayfası)
# ------------------------------------------------------------------
@admin_bp.route("/people/delete", methods=["GET", "POST"])
def person_delete_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            people = (
                conn.execute(
                    text("""
                    SELECT peopleId, primaryName
                    FROM people
                    WHERE primaryName LIKE :q
                    LIMIT 50
                """),
                    {"q": f"%{query}%"},
                )
                .mappings()
                .all()
            )
        else:
            people = (
                conn.execute(
                    text("""
                    SELECT peopleId, primaryName
                    FROM people
                    ORDER BY primaryName
                    LIMIT 20
                """)
                )
                .mappings()
                .all()
            )

    return render_template(
        "admin/delete_generic_menu.html",
        title="Person",
        singular="Person",
        items=people,
        id_field="peopleId",
        name_field="primaryName",
        name_label="Name",
        delete_route="admin.person_delete",
        id_param="people_id",
    )


# ------------------------------------------------------------------
# DELETE PERSON
# ------------------------------------------------------------------
@admin_bp.route("/people/delete/<people_id>", methods=["POST"])
def person_delete(people_id):
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM people WHERE peopleId=:id"), {"id": people_id})
        conn.commit()

    flash("Person deleted!")
    return redirect(url_for("admin.person_delete_menu"))
