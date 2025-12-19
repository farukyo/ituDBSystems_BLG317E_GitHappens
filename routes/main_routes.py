# Main Routes Module
# Handles homepage, about page, quiz, recommendations, and suggestion form.

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from groq import Groq 
import os
import json

main_bp = Blueprint('main', __name__)

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)
@main_bp.route("/")
def index():
    return render_template("home.html")


@main_bp.route("/about")
def about():
    return render_template("about.html")


@main_bp.route("/quiz/setup")
@login_required
def quiz_setup():
    return render_template("quiz_setup.html")

# Quiz Üretme: Formdan gelen verileri alır ve session'a kaydeder
@main_bp.route("/quiz/generate", methods=["POST"])
@login_required
def generate_quiz():
    title = request.form.get("title")
    difficulty = request.form.get("difficulty")
    count = int(request.form.get("question_count", 10)) # Sayıyı aldık

    # Yapay zekaya JSON formatında cevap vermesini emrediyoruz
    prompt = f"""
    Create a detailed and fun trivia quiz with {count} multiple-choice questions about the movie/topic: "{title}".
    Difficulty level: {difficulty}.
    Language: English.

    Guidelines:
    1. Focus on specific details, plot points, characters, and iconic scenes if "{title}" is a movie or book.
    2. Ensure the questions are not generic advice but specific to the facts about "{title}".
    3. The tone should be engaging.
    4. Each question must have exactly 4 options.
    5. Avoid mixing languages; use only English.

    You must respond ONLY with a valid JSON object in this format:
    {{
        "questions": [
            {{
                "question": "Soru metni buraya",
                "options": ["Seçenek 1", "Seçenek 2", "Seçenek 3", "Seçenek 4"],
                "answer": "Doğru olan seçeneğin aynısı"
            }}
        ]
    }}
    """

    try:
        # Groq API Çağrısı
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # Ücretsiz ve çok güçlü bir model
            response_format={"type": "json_object"} # JSON dönmesini garanti eder
        )

        # Yanıtı JSON olarak işle
        raw_response = chat_completion.choices[0].message.content
        quiz_data = json.loads(raw_response)

        # Session'a kaydet
        session["quiz"] = quiz_data
        session.modified = True

        return redirect(url_for("main.quiz_play"))

    except Exception as e:
        print("GROQ AI HATASI:", e)
        flash("Quiz oluşturulurken bir hata oluştu.")
        return redirect(url_for("main.quiz_setup"))


# Quiz Oynama Sayfası
@main_bp.route("/quiz/play")
@login_required
def quiz_play():
    quiz = session.get("quiz")
    if not quiz:
        return redirect(url_for("main.quiz_setup"))

    return render_template("quiz_play.html", quiz=quiz)

# Sonuç Hesaplama
@main_bp.route("/quiz/submit", methods=["POST"])
@login_required
def submit_quiz():
    quiz = session.get("quiz")
    
    # Eğer session düşmüşse veya quiz verisi yoksa ana sayfaya at
    if not quiz or "questions" not in quiz:
        return redirect(url_for("main.quiz_setup"))

    correct = 0
    questions = quiz["questions"]
    total = len(questions)

    for i, q in enumerate(questions):
        # Formdan gelen cevabı al (q0, q1, q2...)
        user_answer = request.form.get(f"q{i}")
        
        # DEBUG: Terminale yazdırarak hangi soruda hata olduğunu görebilirsin
        print(f"Soru {i} için Kullanıcı Cevabı: {user_answer} | Doğru Cevap: {q['answer']}")
        
        if user_answer == q["answer"]:
            correct += 1

    # Skor hesaplama (Bölme hatasını önlemek için total > 0 kontrolü)
    score = round((correct / total) * 100) if total > 0 else 0

    return render_template(
        "quiz_result.html",
        correct=correct,
        total=total,
        score=score
    )


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
