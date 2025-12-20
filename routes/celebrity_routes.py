# Celebrity Routes Module
# Handles celebrity listing and details with 'is_liked' check.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import text
from database.db import engine

celebrity_bp = Blueprint('celebrity', __name__)

@celebrity_bp.route("/celebrities")
def celebrities():
    # Filtre Parametrelerini Al
    search_query = request.args.get('q')
    profession_list = request.args.getlist('profession')
    primary_letter = request.args.get('primary_name')
    birth_filter = request.args.get('birth_year')
    death_filter = request.args.get('death_year')
    order_filter = request.args.get('order_by')

    # Giriş yapmış kullanıcı ID'si (Yoksa -1 veriyoruz ki SQL hata vermesin)
    uid = current_user.id if current_user.is_authenticated else -1

    data = []
    display_sql = "No query executed yet."

    has_filters = any([search_query, profession_list, primary_letter, birth_filter, death_filter, order_filter])

    if has_filters:
        with engine.connect() as conn:
            sql = """
                SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear, pr.professionName,
                       CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
                FROM people p
                LEFT JOIN profession pr ON p.professionId = pr.professionId
                LEFT JOIN user_likes ul ON p.peopleId = ul.entity_id 
                                       AND ul.user_id = :uid 
                                       AND ul.entity_type = 'person'
                WHERE 1=1
            """
            params = {"uid": uid}

            # --- FİLTRELER ---
            if not search_query and not primary_letter:
                sql += " AND p.primaryName REGEXP '^[A-Za-z]'"
                sql += " AND CHAR_LENGTH(p.primaryName) >= 3"
            
            if search_query:
                sql += " AND p.primaryName LIKE :q"
                params["q"] = f"%{search_query}%"

            if profession_list:
                prof_conditions = [f"pr.professionName LIKE :prof_{i}" for i in range(len(profession_list))]
                for i, prof in enumerate(profession_list):
                    params[f"prof_{i}"] = f"%{prof}%"
                sql += " AND (" + " AND ".join(prof_conditions) + ")"
                
            if primary_letter:
                sql += " AND p.primaryName LIKE :letter"
                params["letter"] = f"{primary_letter}%"

            if birth_filter:
                sql += " AND p.birthYear = :byear"
                params["byear"] = int(birth_filter)

            if death_filter:
                sql += " AND p.deathYear = :dyear"
                params["dyear"] = int(death_filter)

            # --- SIRALAMA ---
            if order_filter == "alphabetical":
                sql += " ORDER BY p.primaryName ASC"
            elif order_filter == "age-asc":
                sql += " ORDER BY (CASE WHEN p.deathYear IS NOT NULL THEN (p.deathYear - p.birthYear) ELSE (2025 - p.birthYear) END) ASC"
            elif order_filter == "age-desc":
                sql += " ORDER BY (CASE WHEN p.deathYear IS NOT NULL THEN (p.deathYear - p.birthYear) ELSE (2025 - p.birthYear) END) DESC"
            else:
                sql += " ORDER BY p.primaryName ASC"

            sql += " LIMIT 50"
            
            # Debug için SQL stringini hazırla
            display_sql = sql
            for k, v in params.items():
                display_sql = display_sql.replace(f":{k}", str(v) if isinstance(v, int) else f"'{v}'")

            result = conn.execute(text(sql), params)
            data = result.fetchall()

    title = f"Results for '{search_query}'" if search_query else "Celebrities"
    
    return render_template("celebrities.html", 
                           items=data, 
                           title=title, 
                           selected_professions=profession_list,
                           sql_query=display_sql)

@celebrity_bp.route("/celebrity/<people_id>")
def celebrity_detail(people_id):
    uid = current_user.id if current_user.is_authenticated else -1
    
    with engine.connect() as conn:
        sql = """
            SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear, pr.professionName,
                   CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
            FROM people p
            LEFT JOIN profession pr ON p.professionId = pr.professionId
            LEFT JOIN user_likes ul ON p.peopleId = ul.entity_id 
                                   AND ul.user_id = :uid 
                                   AND ul.entity_type = 'person'
            WHERE p.peopleId = :id
        """
        result = conn.execute(text(sql), {"id": people_id, "uid": uid})
        person = result.fetchone()

        if not person:
            flash("Celebrity not found.")
            return redirect(url_for('celebrity.celebrities'))

    return render_template("celebrity.html", person=person)

@celebrity_bp.route("/like_celebrity", methods=["POST"])
@login_required
def like_celebrity():
    people_id = request.form.get('people_id')
    user_id = current_user.id
    
    with engine.connect() as conn:
        check_sql = """
            SELECT 1 FROM user_likes 
            WHERE user_id = :uid AND entity_id = :eid AND entity_type = 'person'
        """
        result = conn.execute(text(check_sql), {"uid": user_id, "eid": people_id}).fetchone()
        
        if result:
            delete_sql = """
                DELETE FROM user_likes 
                WHERE user_id = :uid AND entity_id = :eid AND entity_type = 'person'
            """
            conn.execute(text(delete_sql), {"uid": user_id, "eid": people_id})
        else:
            insert_sql = """
                INSERT INTO user_likes (user_id, entity_id, entity_type)
                VALUES (:uid, :eid, 'person')
            """
            conn.execute(text(insert_sql), {"uid": user_id, "eid": people_id})
            
        conn.commit()

    return "1"