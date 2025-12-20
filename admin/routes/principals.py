from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp

# -------------------------------------------------
# PRINCIPALS MENU (GENERIC)
# -------------------------------------------------
@admin_bp.route("/principals/menu")
def principals_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Principals",
        singular="Principal",
        add_route="admin.principal_new",
        edit_route="admin.principal_edit_menu",
        delete_route="admin.principal_delete_menu"
    )


# -------------------------------------------------
# NEW PRINCIPAL (ASSIGN PERSON TO TITLE)
# -------------------------------------------------
@admin_bp.route("/principals/new", methods=["GET", "POST"])
def principal_new():

    if request.method == "POST":
        title_name = request.form.get("titleName")
        people_name = request.form.get("peopleName")
        category = request.form.get("category")
        job = request.form.get("job")
        characters = request.form.get("characters")

        if not title_name or not people_name:
            flash("Title name and People name are required.")
            return redirect(url_for("admin.principal_new"))

        with engine.begin() as conn:
            # Title ID bul (movies veya series)
            title_row = conn.execute(
                text("""
                    SELECT movieId AS titleId FROM movies WHERE movieTitle = :name
                    UNION
                    SELECT seriesId AS titleId FROM series WHERE seriesTitle = :name
                    LIMIT 1
                """),
                {"name": title_name}
            ).fetchone()

            # People ID bul
            people_row = conn.execute(
                text("""
                    SELECT peopleId FROM people WHERE primaryName = :name
                    LIMIT 1
                """),
                {"name": people_name}
            ).fetchone()

            if not title_row or not people_row:
                flash("Title or person not found. Please create them first.")
                return redirect(url_for("admin.principal_new"))

            title_id = title_row[0]
            people_id = people_row[0]

            # Duplicate kontrol
            exists = conn.execute(
                text("""
                    SELECT 1 FROM principals
                    WHERE titleId = :t AND peopleId = :p
                """),
                {"t": title_id, "p": people_id}
            ).fetchone()

            if exists:
                flash("This principal already exists.")
                return redirect(url_for("admin.principal_new"))

            # Insert
            conn.execute(
                text("""
                    INSERT INTO principals (titleId, peopleId, category, job, characters)
                    VALUES (:t, :p, :c, :j, :ch)
                """),
                {"t": title_id, "p": people_id, "c": category, "j": job, "ch": characters}
            )

        flash("Principal added successfully.")
        return redirect(url_for("admin.principals_menu"))

    return render_template("admin/principal_form.html", principal=None)

# -------------------------------------------------
# DELETE PRINCIPAL MENU
# -------------------------------------------------
@admin_bp.route("/principals/delete", methods=["GET", "POST"])
def principal_delete_menu():

    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            # Arama varsa: Kişi Adı OR ID OR Film Adı OR Dizi Adı
            principals = conn.execute(
                text("""
                    SELECT
                        p.titleId,
                        p.peopleId,
                        COALESCE(m.movieTitle, s.seriesTitle) AS titleName,
                        pe.primaryName,
                        p.category
                    FROM principals p
                    JOIN people pe ON p.peopleId = pe.peopleId
                    LEFT JOIN movies m ON p.titleId = m.movieId
                    LEFT JOIN series s ON p.titleId = s.seriesId
                    WHERE pe.primaryName LIKE :q
                       OR p.titleId LIKE :q
                       OR m.movieTitle LIKE :q   -- YENİ EKLENDİ: Film adına göre arama
                       OR s.seriesTitle LIKE :q  -- YENİ EKLENDİ: Dizi adına göre arama
                    ORDER BY titleName
                    LIMIT 20
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            # Arama yoksa varsayılan listeleme (Değişiklik yok)
            principals = conn.execute(
                text("""
                    SELECT
                        p.titleId,
                        p.peopleId,
                        COALESCE(m.movieTitle, s.seriesTitle) AS titleName,
                        pe.primaryName,
                        p.category
                    FROM principals p
                    JOIN people pe ON p.peopleId = pe.peopleId
                    LEFT JOIN movies m ON p.titleId = m.movieId
                    LEFT JOIN series s ON p.titleId = s.seriesId
                    ORDER BY titleName
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/principal_delete_menu.html",
        principals=principals
    )

# -------------------------------------------------
# DELETE PRINCIPAL
# -------------------------------------------------
@admin_bp.route(
    "/principals/delete/<title_id>/<people_id>",
    methods=["POST"]
)
def principal_delete(title_id, people_id):

    with engine.begin() as conn:
        conn.execute(
            text("""
                DELETE FROM principals
                WHERE titleId = :t AND peopleId = :p
            """),
            {"t": title_id, "p": people_id}
        )

    flash("Principal deleted successfully.")
    return redirect(url_for("admin.principal_delete_menu"))

# -------------------------------------------------
# EDIT PRINCIPAL MENU
# -------------------------------------------------
@admin_bp.route("/principals/edit", methods=["GET", "POST"])
def principal_edit_menu():

    query = request.form.get("search")

    with engine.connect() as conn:
        if query:
            principals = conn.execute(
                text("""
                    SELECT
                        p.titleId,
                        p.peopleId,
                        COALESCE(m.movieTitle, s.seriesTitle) AS titleName,
                        pe.primaryName,
                        p.category,
                        p.job,
                        p.characters
                    FROM principals p
                    JOIN people pe ON p.peopleId = pe.peopleId
                    LEFT JOIN movies m ON p.titleId = m.movieId
                    LEFT JOIN series s ON p.titleId = s.seriesId
                    WHERE pe.primaryName LIKE :q
                       OR p.titleId LIKE :q
                       OR m.movieTitle LIKE :q
                       OR s.seriesTitle LIKE :q
                    ORDER BY titleName
                    LIMIT 20
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            principals = conn.execute(
                text("""
                    SELECT
                        p.titleId,
                        p.peopleId,
                        COALESCE(m.movieTitle, s.seriesTitle) AS titleName,
                        pe.primaryName,
                        p.category,
                        p.job,
                        p.characters
                    FROM principals p
                    JOIN people pe ON p.peopleId = pe.peopleId
                    LEFT JOIN movies m ON p.titleId = m.movieId
                    LEFT JOIN series s ON p.titleId = s.seriesId
                    ORDER BY titleName
                    LIMIT 20
                """)
            ).mappings().all()

    return render_template(
        "admin/principal_edit_menu.html",
        principals=principals
    )

# -------------------------------------------------
# EDIT PRINCIPAL
# -------------------------------------------------
@admin_bp.route("/principals/edit/<title_id>/<people_id>", methods=["GET", "POST"])
def principal_edit(title_id, people_id):

    if request.method == "POST":
        category = request.form.get("category")
        job = request.form.get("job")
        characters = request.form.get("characters")

        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE principals
                    SET category = :c, job = :j, characters = :ch
                    WHERE titleId = :t AND peopleId = :p
                """),
                {
                    "c": category,
                    "j": job,
                    "ch": characters,
                    "t": title_id,
                    "p": people_id
                }
            )

        flash("Principal updated successfully.")
        return redirect(url_for("admin.principal_edit_menu"))

    with engine.connect() as conn:
        principal = conn.execute(
            text("""
                SELECT
                    p.titleId,
                    p.peopleId,
                    COALESCE(m.movieTitle, s.seriesTitle) AS titleName,
                    pe.primaryName,
                    p.category,
                    p.job,
                    p.characters
                FROM principals p
                JOIN people pe ON p.peopleId = pe.peopleId
                LEFT JOIN movies m ON p.titleId = m.movieId
                LEFT JOIN series s ON p.titleId = s.seriesId
                WHERE p.titleId = :t AND p.peopleId = :p
            """),
            {"t": title_id, "p": people_id}
        ).mappings().first()

    return render_template("admin/principal_form.html", principal=principal)