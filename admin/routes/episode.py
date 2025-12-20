from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp
import random

# ------------------------------------------------------------------
# EPISODES MENU
# ------------------------------------------------------------------
@admin_bp.route("/episodes/menu")
def episode_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Episodes",
        singular="Episode",
        add_route="admin.episode_new",
        edit_route="admin.episode_edit_menu",
        delete_route="admin.episode_delete_menu"
    )


# ------------------------------------------------------------------
# NEW EPISODE
# ------------------------------------------------------------------
@admin_bp.route("/episodes/new", methods=["GET", "POST"])
def episode_new():
    if request.method == "POST":
        ep_title = request.form.get("episodeTitle", "").strip()
        series_title = request.form.get("seriesTitle", "").strip()
        season_no = request.form.get("seasonNumber")
        ep_no = request.form.get("episodeNumber")
        runtime = request.form.get("runtimeMinutes")

        if not ep_title or not series_title:
            flash("Episode title and series title are required.")
            return redirect(url_for("admin.episode_new"))

        season_no = int(season_no) if season_no else None
        ep_no = int(ep_no) if ep_no else None
        runtime = int(runtime) if runtime else None

        with engine.begin() as conn:
            # SERIES KONTROL
            series = conn.execute(
                text("""
                    SELECT seriesId
                    FROM Series
                    WHERE seriesTitle = :t
                    LIMIT 1
                """),
                {"t": series_title}
            ).fetchone()

            if not series:
                flash("Series not found.")
                return redirect(url_for("admin.episode_new"))

            # UNIQUE episodeId
            while True:
                episode_id = f"tt{random.randint(0, 9999999):07d}"
                exists = conn.execute(
                    text("SELECT 1 FROM Episode WHERE episodeId = :id"),
                    {"id": episode_id}
                ).fetchone()
                if not exists:
                    break

            conn.execute(
                text("""
                    INSERT INTO Episode
                    (episodeId, seriesId, seNumber, epNumber, runtimeMinutes, epTitle)
                    VALUES (:id, :sid, :sn, :en, :rt, :t)
                """),
                {
                    "id": episode_id,
                    "sid": series.seriesId,
                    "sn": season_no,
                    "en": ep_no,
                    "rt": runtime,
                    "t": ep_title
                }
            )

        flash("New episode added successfully!")
        return redirect(url_for("admin.episode_menu"))

    return render_template("episode_form.html", episode=None)


# ------------------------------------------------------------------
# EDIT EPISODE
# ------------------------------------------------------------------
@admin_bp.route("/episodes/edit/<episode_id>", methods=["GET", "POST"])
def episode_edit(episode_id):

    with engine.connect() as conn:
        episode = conn.execute(
            text("""
                SELECT 
                    e.episodeId,
                    e.epTitle,
                    e.seNumber,
                    e.epNumber,
                    e.runtimeMinutes,
                    s.seriesTitle
                FROM Episode e
                JOIN Series s ON e.seriesId = s.seriesId
                WHERE e.episodeId = :id
            """),
            {"id": episode_id}
        ).mappings().fetchone()

    if not episode:
        flash("Episode not found.")
        return redirect(url_for("admin.episode_menu"))

    if request.method == "POST":
        ep_title = request.form.get("episodeTitle", "").strip()
        series_title = request.form.get("seriesTitle", "").strip()
        season_no = request.form.get("seasonNumber")
        ep_no = request.form.get("episodeNumber")
        runtime = request.form.get("runtimeMinutes")

        if not ep_title or not series_title:
            flash("Episode title and series title are required.")
            return redirect(url_for("admin.episode_edit", episode_id=episode_id))

        season_no = int(season_no) if season_no else None
        ep_no = int(ep_no) if ep_no else None
        runtime = int(runtime) if runtime else None

        with engine.begin() as conn:
            series = conn.execute(
                text("SELECT seriesId FROM Series WHERE seriesTitle = :t"),
                {"t": series_title}
            ).fetchone()

            if not series:
                flash("Series not found.")
                return redirect(url_for("admin.episode_edit", episode_id=episode_id))

            conn.execute(
                text("""
                    UPDATE Episode
                    SET epTitle = :t,
                        seriesId = :sid,
                        seNumber = :sn,
                        epNumber = :en,
                        runtimeMinutes = :rt
                    WHERE episodeId = :id
                """),
                {
                    "t": ep_title,
                    "sid": series.seriesId,
                    "sn": season_no,
                    "en": ep_no,
                    "rt": runtime,
                    "id": episode_id
                }
            )

        flash("Episode updated successfully!")
        return redirect(url_for("admin.episode_menu"))

    return render_template("episode_form.html", episode=episode)


# ------------------------------------------------------------------
# EDIT EPISODE MENU
# ------------------------------------------------------------------
@admin_bp.route("/episodes/edit", methods=["GET", "POST"])
def episode_edit_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            episodes = conn.execute(
                text("""
                    SELECT episodeId, epTitle
                    FROM Episode
                    WHERE epTitle LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            episodes = conn.execute(
                text("""
                    SELECT episodeId, epTitle
                    FROM Episode
                    ORDER BY epTitle
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/edit_generic_menu.html",
        title="Episodes",
        singular="Episode",
        items=episodes,
        id_field="episodeId",
        name_field="epTitle",
        name_label="Title",
        edit_route="admin.episode_edit",
        id_param="episode_id"
    )


# ------------------------------------------------------------------
# DELETE EPISODE MENU
# ------------------------------------------------------------------
@admin_bp.route("/episodes/delete", methods=["GET", "POST"])
def episode_delete_menu():
    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            episodes = conn.execute(
                text("""
                    SELECT episodeId, epTitle
                    FROM Episode
                    WHERE epTitle LIKE :q
                    LIMIT 50
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            episodes = conn.execute(
                text("""
                    SELECT episodeId, epTitle
                    FROM Episode
                    ORDER BY epTitle
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/delete_generic_menu.html",
        title="Episodes",
        singular="Episode",
        items=episodes,
        id_field="episodeId",
        name_field="epTitle",
        name_label="Title",
        delete_route="admin.episode_delete",
        id_param="episode_id"
    )


# ------------------------------------------------------------------
# DELETE EPISODE
# ------------------------------------------------------------------
@admin_bp.route("/episodes/delete/<episode_id>", methods=["POST"])
def episode_delete(episode_id):
    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM Episode WHERE episodeId = :id"),
            {"id": episode_id}
        )

    flash("Episode deleted successfully!")
    return redirect(url_for("admin.episode_delete_menu"))