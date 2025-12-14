# Main Routes Module
# Handles homepage, about page, quiz, recommendations, and suggestion form.

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route("/")
def index():
    return render_template("home.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/quiz")
@login_required
def quiz():
    return render_template("quiz.html")


@main_bp.route("/recommend")
@login_required
def recommend():
    return render_template("recommend.html")


@main_bp.route("/suggest", methods=["GET", "POST"])
@login_required
def suggest():
    if request.method == "POST":
        subject = request.form.get("subject")
        message_body = request.form.get("message")
        
        # Sender info
        user_email = current_user.email
        user_name = current_user.username
        
        # -------------------------------------------------------
        # MAIL SENDING LOGIC WILL BE ADDED HERE
        # (SMTP or API code to be added in the future)
        # -------------------------------------------------------
        
        flash("Thank you! Your suggestion has been sent successfully.")
        return redirect(url_for('main.index'))
        
    return render_template("suggestion.html")
