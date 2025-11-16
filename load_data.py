import pandas as pd
from database.db import engine


# Faruk'un hazırladığı dosyalar için
CSV_PATH = "clean_dataset.csv"
TABLE_NAME = "series"


if __name__ == "__main__":
    print("CSV okunuyor:", CSV_PATH)
    df = pd.read_csv(CSV_PATH)

    # Opsiyonel: tabloyu baştan oluşturmak istersen if_exists='replace'
    # Eğer var olan tabloya eklemek istersen 'append' kullan
    df.to_sql(TABLE_NAME, con=engine, if_exists="replace", index=False)

    print(f"Veri başarıyla tabloya yazıldı: {TABLE_NAME}")


# Bu dosyayı 1 kere çalıştırırsın:
# python load_data.py


# html içinde veri kullanma

# <h2>Series List</h2>
# <ul>
#     {% for item in series %}
#         <li>
#             {{ item.title }} - {{ item.year }} - {{ item.rating }}
#         </li>
#     {% endfor %}
# </ul>

# movies.html sayfasına veri göndermek istiyorsam :

#  @app.route("/movies")
#  def movies():
#     with engine.connect() as conn:
#         result = conn.execute(text("SELECT * FROM series"))
#         data = result.fetchall()
#     return render_template("movies.html", series=data)
