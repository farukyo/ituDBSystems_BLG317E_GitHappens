# Celebrity Routes Module
# Handles celebrity listing and details with 'is_liked' check.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from sqlalchemy import text
from database.db import engine

celebrity_bp = Blueprint('celebrity', __name__)

@celebrity_bp.route("/celebrities")
def celebrities():
    search_query = request.args.get('q')
    profession_list = request.args.getlist('profession')
    primary_letter = request.args.get('primary_name')
    birth_filter = request.args.get('birth_year')
    death_filter = request.args.get('death_year')
    order_filter = request.args.get('order_by')

    uid = current_user.id if current_user.is_authenticated else -1

    data = []
    display_sql = ""
    page_title = "Celebrities"

    has_filters = any([search_query, profession_list, primary_letter, birth_filter, death_filter, order_filter])

    with engine.connect() as conn:
        

        # --- 1. SENARYO: FİLTRE YOKSA (EN İYİ PROJESİNE GÖRE SIRALA) ---
        if not has_filters:
            sql = """
            SELECT 
                p.peopleId, 
                p.primaryName, 
                p.birthYear, 
                p.deathYear, 
                prof.professionName,
                MAX(r.averageRating) as top_rating, 
                CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
            FROM people p
            JOIN principals pr ON p.peopleId = pr.peopleId
            JOIN ratings r ON pr.titleId = r.titleId
            LEFT JOIN profession prof ON p.professionId = prof.professionId
            LEFT JOIN githappens_users.user_likes ul ON p.peopleId = ul.entity_id 
                                   AND ul.user_id = :uid 
                                   AND ul.entity_type = 'person'
            WHERE r.numVotes > 1000      
            GROUP BY p.peopleId, p.primaryName, p.birthYear, 
            p.deathYear, prof.professionName, ul.user_id
            HAVING COUNT(pr.titleId) >= 1
            ORDER BY top_rating DESC, p.primaryName ASC 
            LIMIT 50
            """
            params = {"uid": uid}
            
            # Sorguyu çalıştır
            result = conn.execute(text(sql), params)
            data = result.fetchall()
            
            # SQL Kodunu Göster
            display_sql = sql.replace(":uid", str(uid))

        else:
            page_title = f"Results for '{search_query}'" if search_query else "Search Results"
            
            sql = """
                SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear, pr.professionName
                FROM people p
                LEFT JOIN profession pr ON p.professionId = pr.professionId
                WHERE 1=1
            """
            params = {}

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

            if order_filter == "alphabetical":
                sql += " ORDER BY p.primaryName ASC"
            elif order_filter == "age-asc":
                sql += " ORDER BY (CASE WHEN p.deathYear IS NOT NULL THEN (p.deathYear - p.birthYear) ELSE (2025 - p.birthYear) END) ASC"
            elif order_filter == "age-desc":
                sql += " ORDER BY (CASE WHEN p.deathYear IS NOT NULL THEN (p.deathYear - p.birthYear) ELSE (2025 - p.birthYear) END) DESC"
            else:
                sql += " ORDER BY p.primaryName ASC"

            sql += " LIMIT 50"
            
            result = conn.execute(text(sql), params)
            data = result.fetchall()

            display_sql = sql
            for k, v in params.items():
                display_sql = display_sql.replace(f":{k}", str(v) if isinstance(v, int) else f"'{v}'")

    
    return render_template("celebrities.html", 
                           items=data, 
                           title=page_title, 
                           selected_professions=profession_list,
                           sql_query=display_sql)

@celebrity_bp.route("/celebrity/<people_id>")
def celebrity_detail(people_id):
    uid = current_user.id if current_user.is_authenticated else -1
    
    with engine.connect() as conn:

        sql_person = """
            SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear, pr.professionName,
                   CASE WHEN ul.user_id IS NOT NULL THEN 1 ELSE 0 END as is_liked
            FROM people p
            LEFT JOIN profession pr ON p.professionId = pr.professionId
            LEFT JOIN githappens_users.user_likes ul ON p.peopleId = ul.entity_id 
                                   AND ul.user_id = :uid 
                                   AND ul.entity_type = 'person'
            WHERE p.peopleId = :id
        """
        result = conn.execute(text(sql_person), {"id": people_id, "uid": uid})
        person = result.fetchone()

        if not person:
            flash("Celebrity not found.")
            return redirect(url_for('celebrity.celebrities'))
            
        sql_works = """
            SELECT * FROM (
                -- 1. MOVIES
                SELECT m.movieId as id, m.movieTitle as title, 
                m.startYear, r.averageRating, 'movie' as type
                FROM movies m
                JOIN principals pr ON m.movieId = pr.titleId
                JOIN ratings r ON m.movieId = r.titleId
                WHERE pr.peopleId = :pid AND r.numVotes > 1000

                UNION ALL

                -- 2. SERIES
                SELECT s.seriesId as id, s.seriesTitle as title, 
                s.startYear, r.averageRating, 'series' as type
                FROM series s
                JOIN principals pr ON s.seriesId = pr.titleId
                JOIN ratings r ON s.seriesId = r.titleId
                WHERE pr.peopleId = :pid AND r.numVotes > 1000
            ) as combined_works
            ORDER BY averageRating DESC
            LIMIT 8
        """
        best_works = conn.execute(text(sql_works), {"pid": people_id}).fetchall()
        display_sql = "-- 1. Fetch Person Details\n" + sql_person.replace(":id", f"'{people_id}'").replace(":uid", str(uid))
        display_sql += "\n\n-- 2. Fetch Top Rated Works (Union of Movies, Series, Episodes)\n" + sql_works.replace(":pid", f"'{people_id}'")

    return render_template("celebrity.html", person=person, best_works=best_works, sql_query=display_sql)


@celebrity_bp.route("/like_celebrity", methods=["POST"])
@login_required
def like_celebrity():
    people_id = request.form.get('people_id')
    user_id = current_user.id
    
    with engine.connect() as conn:
        check_sql = """
            SELECT 1 FROM githappens_users.user_likes 
            WHERE user_id = :uid AND entity_id = :eid AND entity_type = 'person'
        """
        result = conn.execute(text(check_sql), {"uid": user_id, "eid": people_id}).fetchone()
        
        if result:
            delete_sql = """
                DELETE FROM githappens_users.user_likes 
                WHERE user_id = :uid AND entity_id = :eid AND entity_type = 'person'
            """
            conn.execute(text(delete_sql), {"uid": user_id, "eid": people_id})
        else:
            insert_sql = """
                INSERT INTO githappens_users.user_likes (user_id, entity_id, entity_type)
                VALUES (:uid, :eid, 'person')
            """
            conn.execute(text(insert_sql), {"uid": user_id, "eid": people_id})
            
        conn.commit()

    return "1"