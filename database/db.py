import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}", echo=True
)


# env dosyası herkesin kendine özel DB_USER, DB_PASSWORD yazdığı dosya
# .env diye dosya açıp şunları kendi bilgilerinizle doldurun :
# DB_USER=root
# DB_PASSWORD=buraya_senin_mysql_sifren
# DB_HOST=localhost
# DB_NAME=tvseries

# gitignore dosyasında zaten .env var otomatik ignorelicak o dosyayı projeye eklemicekmiş
