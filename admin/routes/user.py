from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import text
from database.db import engine
from admin import admin_bp
from werkzeug.security import generate_password_hash

# ==========================================================
# USER MENU
# ==========================================================
@admin_bp.route("/users/menu")
def user_menu():
    return render_template(
        "admin/manage_generic.html",
        title="Users",
        singular="User",
        add_route="admin.user_new",
        edit_route="admin.user_edit_menu",
        delete_route="admin.user_delete_menu"
    )


# ==========================================================
# NEW USER
# ==========================================================
@admin_bp.route("/users/new", methods=["GET", "POST"])
def user_new():

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        score = request.form.get("score", 0)
        is_admin = request.form.get("is_admin") == "on"

        if not username or not email or not password:
            flash("Username, email, and password are required.")
            return redirect(url_for("admin.user_new"))

        with engine.begin() as conn:
            # Check duplicate username or email
            exists = conn.execute(
                text("""
                    SELECT 1 FROM githappens_users.users 
                    WHERE username = :u OR email = :e
                """),
                {"u": username, "e": email}
            ).fetchone()

            if exists:
                flash("Username or email already exists.")
                return redirect(url_for("admin.user_new"))

            # Hash password
            password_hash = generate_password_hash(password)

            # Insert user
            conn.execute(
                text("""
                    INSERT INTO githappens_users.users 
                    (username, email, password_hash, dob, gender, score, is_admin)
                    VALUES (:u, :e, :p, :d, :g, :s, :a)
                """),
                {
                    "u": username,
                    "e": email,
                    "p": password_hash,
                    "d": dob if dob else None,
                    "g": gender if gender else None,
                    "s": int(score) if score else 0,
                    "a": is_admin
                }
            )

        flash("User created successfully!")
        return redirect(url_for("admin.user_menu"))

    return render_template("admin/user_form.html", user=None)


# ==========================================================
# EDIT USER MENU
# ==========================================================
@admin_bp.route("/users/edit", methods=["GET", "POST"])
def user_edit_menu():
    query = request.form.get("search", "")

    with engine.connect() as conn:
        if query:
            users = conn.execute(
                text("""
                    SELECT id, username, email, dob, gender, score, is_admin
                    FROM githappens_users.users
                    WHERE username LIKE :q OR email LIKE :q
                    ORDER BY username
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            users = conn.execute(
                text("""
                    SELECT id, username, email, dob, gender, score, is_admin
                    FROM githappens_users.users
                    ORDER BY username
                    LIMIT 50
                """)
            ).mappings().all()

    return render_template("admin/user_edit_menu.html", users=users)


# ==========================================================
# EDIT USER
# ==========================================================
@admin_bp.route("/users/edit/<int:user_id>", methods=["GET", "POST"])
def user_edit(user_id):

    with engine.connect() as conn:
        user = conn.execute(
            text("""
                SELECT id, username, email, dob, gender, score, is_admin
                FROM githappens_users.users
                WHERE id = :id
            """),
            {"id": user_id}
        ).mappings().first()

    if not user:
        flash("User not found.")
        return redirect(url_for("admin.user_edit_menu"))

    if request.method == "POST":
        email = request.form.get("email")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        score = request.form.get("score", 0)
        is_admin = request.form.get("is_admin") == "on"
        new_password = request.form.get("new_password")

        if not email:
            flash("Email is required.")
            return redirect(url_for("admin.user_edit", user_id=user_id))

        with engine.begin() as conn:
            # Update user
            if new_password:
                password_hash = generate_password_hash(new_password)
                conn.execute(
                    text("""
                        UPDATE githappens_users.users
                        SET email = :e, dob = :d, gender = :g, score = :s,
                            is_admin = :a, password_hash = :p
                        WHERE id = :id
                    """),
                    {
                        "e": email,
                        "d": dob if dob else None,
                        "g": gender if gender else None,
                        "s": int(score) if score else 0,
                        "a": is_admin,
                        "p": password_hash,
                        "id": user_id
                    }
                )
            else:
                conn.execute(
                    text("""
                        UPDATE githappens_users.users
                        SET email = :e, dob = :d, gender = :g, score = :s, is_admin = :a
                        WHERE id = :id
                    """),
                    {
                        "e": email,
                        "d": dob if dob else None,
                        "g": gender if gender else None,
                        "s": int(score) if score else 0,
                        "a": is_admin,
                        "id": user_id
                    }
                )

        flash("User updated successfully!")
        return redirect(url_for("admin.user_edit_menu"))

    return render_template("admin/user_form.html", user=user)


# ==========================================================
# DELETE USER MENU
# ==========================================================
@admin_bp.route("/users/delete", methods=["GET", "POST"])
def user_delete_menu():
    query = request.form.get("search", "")

    with engine.connect() as conn:
        if query:
            users = conn.execute(
                text("""
                    SELECT id, username, email, score
                    FROM githappens_users.users
                    WHERE username LIKE :q OR email LIKE :q
                    ORDER BY username
                """),
                {"q": f"%{query}%"}
            ).mappings().all()
        else:
            users = conn.execute(
                text("""
                    SELECT id, username, email, score
                    FROM githappens_users.users
                    ORDER BY username
                    LIMIT 50
                """)
            ).mappings().all()

    return render_template("admin/user_delete_menu.html", users=users)


# ==========================================================
# DELETE USER
# ==========================================================
@admin_bp.route("/users/delete/<int:user_id>", methods=["POST"])
def user_delete(user_id):

    with engine.begin() as conn:
        # Check if user has associated data (eğer tablolar varsa kontrol et)
        has_data = False
        
        try:
            result = conn.execute(
                text("""
                    SELECT 1 FROM githappens_users.reviews WHERE user_id = :id
                    UNION
                    SELECT 1 FROM githappens_users.watchlist WHERE user_id = :id
                    UNION
                    SELECT 1 FROM githappens_users.user_ratings WHERE user_id = :id
                    LIMIT 1
                """),
                {"id": user_id}
            ).fetchone()
            has_data = result is not None
        except:
            # Tablolar yoksa kontrol yapma
            pass

        if has_data:
            flash("Cannot delete: User has associated data (reviews, watchlist, ratings).")
            return redirect(url_for("admin.user_delete_menu"))

        # Delete user
        conn.execute(
            text("DELETE FROM githappens_users.users WHERE id = :id"),
            {"id": user_id}
        )

    flash("User deleted successfully!")
    return redirect(url_for("admin.user_delete_menu"))