import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()  # herkesin kendi .env dosyasını yükler

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME")

SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    future=True
)



# env dosyası herkesin kendine özel DB_USER, DB_PASSWORD yazdığı dosya 
# .env diye dosya açıp şunları kendi bilgilerinizle doldurun : 
# DB_USER=root
# DB_PASSWORD=buraya_senin_mysql_sifren
# DB_HOST=localhost
# DB_NAME=tvseries

# gitignore dosyasında zaten .env var otomatik ignorelicak o dosyayı projeye eklemicekmiş