from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import admin_bp
from database.db import engine
from sqlalchemy import text
import random
import string
def generate_people_id():
    return "nm" + "".join(random.choices(string.digits, k=8))

# Yardımcı: admin kontrolü decorator'ü
#def admin_required(fn):
#    from functools import wraps
#    @wraps(fn)
#    def wrapper(*args, **kwargs):
#        if not current_user.is_authenticated:
#            return redirect(url_for("login"))
#        if current_user.username != "admin":
#            flash("You do not have permission to access this page.")
#           return redirect(url_for("index"))
#        return fn(*args, **kwargs)
#   return wrapper

# Admin ana sayfa
@admin_bp.route("/")
#@login_required
#@admin_required
def index():
    return render_template("index.html")

# PEOPLE - listeleme
@admin_bp.route("/people")
#@login_required
#@admin_required
def people_list():
    with engine.connect() as conn:
        sql = text("SELECT peopleId, primaryName, birthYear, deathYear FROM people ORDER BY primaryName LIMIT 200")
        result = conn.execute(sql)
        people = result.fetchall()
    return render_template("people_list.html", people=people)

# PEOPLE - yeni ekleme (GET form, POST insert)
@admin_bp.route("/people/new", methods=["GET", "POST"])
#@login_required
#@admin_required
def person_new():
    if request.method == "POST":
        people_id = generate_people_id()
        name = request.form.get("primaryName")
        birth = request.form.get("birthYear") or None
        death = request.form.get("deathYear") or None

        with engine.connect() as conn:
            insert_sql = text(
                "INSERT INTO people (peopleId, primaryName, birthYear, deathYear) VALUES (:id, :name, :birth, :death)"
            )
            conn.execute(insert_sql, {"id": people_id, "name": name, "birth": birth, "death": death})
            conn.commit()
        flash("Person created.")
        return redirect(url_for("admin.people_list"))
    return render_template("person_form.html", person=None)

# PEOPLE - düzenleme
@admin_bp.route("/people/<people_id>/edit", methods=["GET", "POST"])
#@login_required
#@admin_required
def person_edit(people_id):
    with engine.connect() as conn:
        if request.method == "POST":
            name = request.form.get("primaryName")
            birth = request.form.get("birthYear") or None
            death = request.form.get("deathYear") or None
            update_sql = text(
                "UPDATE people SET primaryName = :name, birthYear = :birth, deathYear = :death WHERE peopleId = :id"
            )
            conn.execute(update_sql, {"name": name, "birth": birth, "death": death, "id": people_id})
            conn.commit()
            flash("Person updated.")
            return redirect(url_for("admin.people_list"))

        select_sql = text("SELECT peopleId, primaryName, birthYear, deathYear FROM people WHERE peopleId = :id")
        res = conn.execute(select_sql, {"id": people_id})
        person = res.fetchone()
    if not person:
        flash("Person not found.")
        return redirect(url_for("admin.people_list"))
    return render_template("person_form.html", person=person)


# People - silme
@admin_bp.route("/people/<people_id>/delete", methods=["POST"])
#@login_required
#@admin_required
def person_delete(people_id):
    with engine.connect() as conn:
        delete_sql = text("DELETE FROM people WHERE peopleId = :id")
        conn.execute(delete_sql, {"id": people_id})
        conn.commit()
    flash("Person deleted.")
    return redirect(url_for("admin.people_list"))