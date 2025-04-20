# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL bağlantı URL'si
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@localhost:5432/netflix_db"

# Formatı: postgresql://kullanici_adi:parola@host:port/veritabani_adi

# Veritabanı motorunu oluştur
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Oturum oluşturucu
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Temel model sınıfı
Base = declarative_base()

# Veritabanı bağlantısı için dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()