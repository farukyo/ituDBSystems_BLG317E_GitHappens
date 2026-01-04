from flask import render_template
from admin import admin_bp


@admin_bp.route("/")
def admin_home():
    return render_template("admin/index.html")
