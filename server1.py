from flask import Flask, render_template

app= Flask(__name__)

@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/information")
def information_page():
    return render_template("information.html")

@app.route("/quiz")
def quiz_page():
    return render_template("quiz.html")

@app.route("/recommend")
def recommend_page():
    return render_template("recommend.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
