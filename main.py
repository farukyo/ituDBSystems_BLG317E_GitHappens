from flask import Flask, render_template, request
from database.db import engine
from sqlalchemy import text


app = Flask(__name__)


@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")


@app.route("/recommend")
def recommend_page():
    return render_template("recommend.html")

@app.route("/movies")
def movies_page():
    search_query = request.args.get('q')  # Kullanıcının girdiği kelimeyi alır (Örn: 'real')
    
    with engine.connect() as conn:
        if search_query:
            # 1. SQL Sorgusu: ':term' adında bir değişken bekler.
            sql_query = text("SELECT * FROM genre WHERE description LIKE :term LIMIT 100")
            
            # SQL'e gönderilen parametre adı 'term' olmalıdır.
            result = conn.execute(sql_query, {"term": f"%{search_query}%"})
            
            page_title = f"'{search_query}' için sonuçlar"
        
        else:
            # Arama yapılmazsa...
            sql_query = text("SELECT * FROM genre LIMIT 50")
            result = conn.execute(sql_query)
            page_title = "Tüm Film Türleri"
        
        data = result.fetchall()
    return render_template("movies.html", items=data, title=page_title)

@app.route("/series")
def series_page():
    return render_template("series.html")


@app.route("/celebrities")
def celebrities_page():
    return render_template("celebrities.html")


@app.route("/user")
def user_page():
    return render_template("user.html")


@app.route("/suggest")
def suggest_page():
    return render_template("suggestion.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
