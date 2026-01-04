from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp
import random


# ------------------------------------------------------------------
# SERIES MENU
# ------------------------------------------------------------------
@admin_bp.route("/series/menu")
def series_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Series",
        singular="Series",
        add_route="admin.series_new",
        edit_route="admin.series_edit_menu",
        delete_route="admin.series_delete_menu",
    )


# ------------------------------------------------------------------
# NEW SERIES
# ------------------------------------------------------------------
@admin_bp.route("/series/new", methods=["GET", "POST"])
def series_new():
    if request.method == "POST":
        title = request.form["seriesTitle"]
        title_type = request.form.get("titleType")
        start_year = request.form.get("startYear")
        end_year = request.form.get("endYear")
        runtime = request.form.get("runtimeMinutes")
        is_adult = 1 if request.form.get("isAdult") else 0

        # Tip dönüşümleri
        start_year = int(start_year) if start_year else None
        runtime = int(runtime) if runtime else None
        end_year = int(end_year) if end_year else None

        with engine.begin() as conn:  # transaction
            # UNIQUE ID üret (PARENT tabloya göre)
            while True:
                candidate_id = f"tt{random.randint(0, 9999999):07d}"
                exists = conn.execute(
                    text("SELECT 1 FROM all_titles WHERE titleId = :id"),
                    {"id": candidate_id},
                ).fetchone()
                if not exists:
                    break

            # 1️⃣ PARENT TABLO
            conn.execute(
                text("""
                    INSERT INTO all_titles (titleId)
                    VALUES (:id)
                """),
                {"id": candidate_id},
            )

            # 2️⃣ CHILD TABLO
            conn.execute(
                text("""
                    INSERT INTO series
                    (seriesId, seriesTitle, titleType, startYear, endYear, runtimeMinutes, isAdult)
                    VALUES (:id, :t, :tt, :sy, :ey, :rt, :ia)
                """),
                {
                    "id": candidate_id,
                    "t": title,
                    "tt": title_type,
                    "sy": start_year,
                    "ey": end_year,
                    "rt": runtime,
                    "ia": is_adult,
                },
            )

        flash("New series added successfully!")

    return render_template("series_form.html", series=None)


# ------------------------------------------------------------------
# EDIT SERIES
# ------------------------------------------------------------------
@admin_bp.route("/series/edit/<series_id>", methods=["GET", "POST"])
def series_edit(series_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT seriesId, seriesTitle, titleType, startYear,
                       endYear, runtimeMinutes, isAdult
                FROM series
                WHERE seriesId = :id
            """),
            {"id": series_id},
        )
        series = result.fetchone()

    if request.method == "POST":
        title = request.form["seriesTitle"]
        title_type = request.form.get("titleType") or None
        start_year = request.form.get("startYear") or None
        end_year = request.form.get("endYear") or None
        runtime = request.form.get("runtimeMinutes") or None
        is_adult = 1 if request.form.get("isAdult") else 0

        with engine.connect() as conn:
            conn.execute(
                text("""
                    UPDATE series
                    SET seriesTitle = :t,
                        titleType = :tt,
                        startYear = :sy,
                        endYear = :ey,
                        runtimeMinutes = :rt,
                        isAdult = :ia
                    WHERE seriesId = :id
                """),
                {
                    "t": title,
                    "tt": title_type,
                    "sy": start_year or None,
                    "ey": end_year or None,
                    "rt": runtime or None,
                    "ia": is_adult,
                    "id": series_id,
                },
            )
            conn.commit()

        flash("Series updated!")
        return redirect(url_for("admin.series_edit_menu"))

    return render_template("series_form.html", series=series)


# ------------------------------------------------------------------
# EDIT SERIES MENU (Search)
# ------------------------------------------------------------------
@admin_bp.route("/series/edit", methods=["GET", "POST"])
def series_edit_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            series = (
                conn.execute(
                    text("""
                    SELECT seriesId, seriesTitle
                    FROM series
                    WHERE seriesTitle LIKE :q
                    LIMIT 50
                """),
                    {"q": f"%{query}%"},
                )
                .mappings()
                .all()
            )
        else:
            series = (
                conn.execute(
                    text("""
                    SELECT seriesId, seriesTitle
                    FROM series
                    ORDER BY seriesTitle
                    LIMIT 20
                """)
                )
                .mappings()
                .all()
            )

    return render_template(
        "admin/edit_generic_menu.html",
        title="Series",
        singular="Series",
        items=series,
        id_field="seriesId",
        name_field="seriesTitle",
        name_label="Title",
        edit_route="admin.series_edit",
        id_param="series_id",
    )


# ------------------------------------------------------------------
# DELETE SERIES MENU (Search)
# ------------------------------------------------------------------
@admin_bp.route("/series/delete", methods=["GET", "POST"])
def series_delete_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            series = (
                conn.execute(
                    text("""
                    SELECT seriesId, seriesTitle
                    FROM series
                    WHERE seriesTitle LIKE :q
                    LIMIT 50
                """),
                    {"q": f"%{query}%"},
                )
                .mappings()
                .all()
            )
        else:
            series = (
                conn.execute(
                    text("""
                    SELECT seriesId, seriesTitle
                    FROM series
                    ORDER BY seriesTitle
                    LIMIT 20
                """)
                )
                .mappings()
                .all()
            )

    return render_template(
        "admin/delete_generic_menu.html",
        title="Series",
        singular="Series",
        items=series,
        id_field="seriesId",
        name_field="seriesTitle",
        name_label="Title",
        delete_route="admin.series_delete",
        id_param="series_id",
    )


# ------------------------------------------------------------------
# DELETE SERIES
# ------------------------------------------------------------------
@admin_bp.route("/series/delete/<series_id>", methods=["POST"])
def series_delete(series_id):
    with engine.begin() as conn:
        # 1️⃣ CHILD
        conn.execute(text("DELETE FROM series WHERE seriesId = :id"), {"id": series_id})

        # 2️⃣ PARENT
        conn.execute(
            text("DELETE FROM all_titles WHERE titleId = :id"), {"id": series_id}
        )

    flash("Series deleted successfully!")
    return redirect(url_for("admin.series_delete_menu"))
