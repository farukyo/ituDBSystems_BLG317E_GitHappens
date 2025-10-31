from flask import Flask, render_template

app= Flask(__name__)

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
    return render_template("movies.html")

@app.route("/series")
def series_page():
    return render_template("series.html")

@app.route("/celebrities")
def celebrities_page():
    return render_template("celebrities.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
