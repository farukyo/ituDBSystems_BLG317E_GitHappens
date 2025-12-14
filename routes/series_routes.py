# Series Routes Module
# Handles series listing page with search functionality and AJAX support.

from flask import Blueprint, render_template, request
from sqlalchemy import text
from database.db import engine

series_bp = Blueprint('series', __name__)


@series_bp.route("/series")
def series():
    search_query = request.args.get('q')

    with engine.connect() as conn:
        sql = "SELECT seriesId, seriesTitle, titleType, startYear, endYear, runtimeMinutes, isAdult FROM series WHERE 1=1"
        params = {}

        if search_query:
            sql += " AND seriesTitle LIKE :q"
            params["q"] = f"%{search_query}%"

        sql += " ORDER BY seriesTitle LIMIT 100;"
        result = conn.execute(text(sql), params)
        data = result.fetchall()

    # AJAX request check
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        html_snippets = ""
        for row in data:
            html_snippets += f"""
            <div class="series-card">
                <h3>{row.seriesTitle}</h3>
                <p class="series-genre">N/A</p>
                <p class="series-likes">Liked by 0 users</p>
            </div>
            """
        return html_snippets

    page_title = f"Results for '{search_query}'" if search_query else "All Series"
    return render_template("series.html", items=data, title=page_title)
