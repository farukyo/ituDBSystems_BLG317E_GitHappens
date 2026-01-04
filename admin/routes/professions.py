from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import text
from database.db import engine
from admin import admin_bp


# ==========================================================
# PROFESSIONS MENU
# ==========================================================
@admin_bp.route("/professions/menu")
def professions_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Professions",
        singular="Profession",
        add_route="admin.profession_new",
        edit_route="admin.profession_edit_menu",
        delete_route="admin.profession_delete_menu",
        extra_route="admin.profession_assign",
        extra_label="Assign Professions",
    )


# ==========================================================
# NEW PROFESSION (Insert into profession_dictionary)
# ==========================================================
@admin_bp.route("/professions/new", methods=["GET", "POST"])
def profession_new():
    if request.method == "POST":
        profession_name = request.form.get("professionName")

        if not profession_name:
            flash("Profession name is required.")
            return redirect(url_for("admin.profession_new"))

        with engine.begin() as conn:
            # Check duplicate
            exists = conn.execute(
                text("SELECT 1 FROM profession_dictionary WHERE name = :name"),
                {"name": profession_name},
            ).fetchone()

            if exists:
                flash("Profession already exists.")
                return redirect(url_for("admin.profession_new"))

            # Insert
            conn.execute(
                text("INSERT INTO profession_dictionary (name) VALUES (:name)"),
                {"name": profession_name},
            )

        flash("Profession added successfully!")
        return redirect(url_for("admin.professions_menu"))

    return render_template("admin/profession_form.html", profession=None)


# ==========================================================
# EDIT PROFESSION MENU
# ==========================================================
@admin_bp.route("/professions/edit", methods=["GET", "POST"])
def profession_edit_menu():
    query = request.form.get("search", "")

    with engine.connect() as conn:
        if query:
            professions = (
                conn.execute(
                    text("""
                    SELECT id as professionId, name as professionName 
                    FROM profession_dictionary
                    WHERE name LIKE :q
                    ORDER BY name
                """),
                    {"q": f"%{query}%"},
                )
                .mappings()
                .all()
            )
        else:
            professions = (
                conn.execute(
                    text("""
                    SELECT id as professionId, name as professionName 
                    FROM profession_dictionary
                    ORDER BY name
                """)
                )
                .mappings()
                .all()
            )

    return render_template(
        "admin/edit_generic_menu.html",
        title="Professions",
        singular="Profession",
        items=professions,
        id_field="professionId",
        name_field="professionName",
        name_label="Profession Name",
        edit_route="admin.profession_edit",
        id_param="profession_id",
    )


# ==========================================================
# EDIT PROFESSION
# ==========================================================
@admin_bp.route("/professions/edit/<int:profession_id>", methods=["GET", "POST"])
def profession_edit(profession_id):
    with engine.connect() as conn:
        prof = (
            conn.execute(
                text(
                    "SELECT id as professionId, name as professionName FROM profession_dictionary WHERE id = :id"
                ),
                {"id": profession_id},
            )
            .mappings()
            .first()
        )

    if not prof:
        flash("Profession not found.")
        return redirect(url_for("admin.profession_edit_menu"))

    if request.method == "POST":
        new_name = request.form.get("professionName")

        if not new_name:
            flash("Profession name cannot be empty.")
            return redirect(
                url_for("admin.profession_edit", profession_id=profession_id)
            )

        with engine.begin() as conn:
            conn.execute(
                text("UPDATE profession_dictionary SET name = :name WHERE id = :id"),
                {"name": new_name, "id": profession_id},
            )

        flash("Profession updated successfully!")
        return redirect(url_for("admin.profession_edit_menu"))

    return render_template("admin/profession_form.html", profession=prof)


# ==========================================================
# DELETE PROFESSION MENU
# ==========================================================
@admin_bp.route("/professions/delete", methods=["GET", "POST"])
def profession_delete_menu():
    query = request.form.get("search", "")

    with engine.connect() as conn:
        if query:
            professions = (
                conn.execute(
                    text("""
                    SELECT id as professionId, name as professionName 
                    FROM profession_dictionary
                    WHERE name LIKE :q
                    ORDER BY name
                """),
                    {"q": f"%{query}%"},
                )
                .mappings()
                .all()
            )
        else:
            professions = (
                conn.execute(
                    text("""
                    SELECT id as professionId, name as professionName 
                    FROM profession_dictionary
                    ORDER BY name
                """)
                )
                .mappings()
                .all()
            )

    return render_template(
        "admin/delete_generic_menu.html",
        title="Professions",
        singular="Profession",
        items=professions,
        id_field="professionId",
        name_field="professionName",
        name_label="Profession Name",
        delete_route="admin.profession_delete",
        id_param="profession_id",
    )


# ==========================================================
# DELETE PROFESSION (Check FK in profession_assignments)
# ==========================================================
@admin_bp.route("/professions/delete/<int:profession_id>", methods=["POST"])
def profession_delete(profession_id):
    with engine.begin() as conn:
        # Check if used in profession_assignments (kolon: profession_dict_id)
        in_use = conn.execute(
            text(
                "SELECT 1 FROM profession_assignments WHERE profession_dict_id = :id LIMIT 1"
            ),
            {"id": profession_id},
        ).fetchone()

        if in_use:
            flash("Cannot delete: This profession is assigned to people.")
            return redirect(url_for("admin.profession_delete_menu"))

        # Delete
        conn.execute(
            text("DELETE FROM profession_dictionary WHERE id = :id"),
            {"id": profession_id},
        )

    flash("Profession deleted successfully!")
    return redirect(url_for("admin.profession_delete_menu"))


# ==========================================================
# ASSIGN PROFESSIONS TO PERSON (using profession_assignments)
# ==========================================================
@admin_bp.route("/professions/assign", methods=["GET", "POST"])
def profession_assign():
    if request.method == "POST":
        person_name = request.form.get("personName")
        selected_professions = request.form.getlist("professions")

        if not person_name:
            flash("Person name is required.")
            return redirect(url_for("admin.profession_assign"))

        with engine.begin() as conn:
            # Find peopleId by name
            person = conn.execute(
                text("SELECT peopleId FROM people WHERE primaryName = :name LIMIT 1"),
                {"name": person_name},
            ).fetchone()

            if not person:
                flash("Person not found.")
                return redirect(url_for("admin.profession_assign"))

            people_id = person[0]

            # Delete existing assignments
            conn.execute(
                text("DELETE FROM profession_assignments WHERE peopleId = :id"),
                {"id": people_id},
            )

            # Insert selected professions (kolon: profession_dict_id)
            for prof_id in selected_professions:
                conn.execute(
                    text("""
                        INSERT INTO profession_assignments (peopleId, profession_dict_id)
                        VALUES (:pid, :profid)
                    """),
                    {"pid": people_id, "profid": int(prof_id)},
                )

        flash("Professions assigned successfully!")
        return redirect(url_for("admin.professions_menu"))

    # GET: Show form with all professions
    with engine.connect() as conn:
        all_professions = (
            conn.execute(
                text(
                    "SELECT id as professionId, name as professionName FROM profession_dictionary ORDER BY name"
                )
            )
            .mappings()
            .all()
        )

    return render_template(
        "admin/profession_assign.html",
        professions=all_professions,
        current_professions=[],
    )


# ==========================================================
# GET CURRENT PROFESSIONS FOR PERSON (AJAX)
# ==========================================================
@admin_bp.route("/professions/current")
def profession_current():
    person_name = request.args.get("name")

    if not person_name:
        return jsonify({"professionIds": []}), 400

    with engine.connect() as conn:
        # Find person
        person = conn.execute(
            text("SELECT peopleId FROM people WHERE primaryName = :name LIMIT 1"),
            {"name": person_name},
        ).fetchone()

        if not person:
            return jsonify({"professionIds": []}), 404

        people_id = person[0]

        # Get assigned professions (kolon: profession_dict_id)
        professions = conn.execute(
            text("""
                SELECT profession_dict_id 
                FROM profession_assignments 
                WHERE peopleId = :id
            """),
            {"id": people_id},
        ).fetchall()

        prof_ids = [p[0] for p in professions]

    return jsonify({"professionIds": prof_ids})
