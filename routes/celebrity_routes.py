# Celebrity Routes Module
# Handles celebrity listing with search, profession filtering, and sorting options.

from flask import Blueprint, render_template, request, redirect, url_for, flash
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

    data = []
    display_sql = "No query executed yet."

    has_filters = any([
        search_query, 
        profession_list, 
        primary_letter, 
        birth_filter, 
        death_filter, 
        order_filter
    ])

    if has_filters:
        with engine.connect() as conn:
            sql = """
                SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear, pr.professionName 
                FROM people p
                LEFT JOIN profession pr ON p.professionId = pr.professionId
                WHERE 1=1
            """
            params = {}

            if not search_query and not primary_letter:
                sql += " AND p.primaryName REGEXP '^[A-Za-z]'"
                sql += " AND CHAR_LENGTH(p.primaryName) >= 3"
                sql += " AND p.primaryName REGEXP '[A-Za-z]{2,}'"
                sql += " AND p.primaryName NOT REGEXP '^[A-Za-z][ ._$/0-9\\'-]'"
        
            if search_query:
                sql += " AND p.primaryName LIKE :q"
                params["q"] = f"%{search_query}%"

            if profession_list:
                prof_conditions = []
                for i, prof in enumerate(profession_list):
                    key = f"prof_{i}"
                    prof_conditions.append(f"pr.professionName LIKE :{key}")
                    params[key] = f"%{prof}%"
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

            display_sql = sql
            for key, value in params.items():
                if isinstance(value, str):
                    display_sql = display_sql.replace(f":{key}", f"'{value}'")
                else:
                    display_sql = display_sql.replace(f":{key}", str(value))

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
    with engine.connect() as conn:
        # Kişiyi ve mesleğini ID'ye göre çeken sorgu
        sql = """
            SELECT p.peopleId, p.primaryName, p.birthYear, p.deathYear, pr.professionName 
            FROM people p
            LEFT JOIN profession pr ON p.professionId = pr.professionId
            WHERE p.peopleId = :id
        """
        result = conn.execute(text(sql), {"id": people_id})
        person = result.fetchone()

        if not person:
            flash("Celebrity not found.")
            return redirect(url_for('celebrity.celebrities'))

    return render_template("celebrity.html", person=person)