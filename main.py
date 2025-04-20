from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from typing import List
from .models import User, Movie, watch_history
from .schemas import UserCreate, User as UserSchema, MovieCreate, Movie as MovieSchema, WatchHistory
from .database import engine, get_db
from .recommender import MovieRecommender
from sqlalchemy import inspect

# Veritabanı tablolarını oluştur
from . import models  # Base erişimi için
models.Base.metadata.create_all(bind=engine)

# FastAPI uygulamasını oluştur
app = FastAPI(
    title="Netflix Öneri Sistemi",
    description="Film önerileri için REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

recommender = MovieRecommender()

# Ana sayfa
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Netflix Öneri Sistemi API'sine Hoş Geldiniz!",
        "endpoints": {
            "docs": "/docs",
            "users": "/users/",
            "movies": "/movies/",
            "recommendations": "/users/{user_id}/recommendations/"
        }
    }

# Kullanıcı işlemleri
@app.post("/users/", response_model=UserSchema, tags=["Users"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/users/", response_model=List[UserSchema], tags=["Users"])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()

# Film işlemleri
@app.post("/movies/", response_model=MovieSchema, tags=["Movies"])
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    new_movie = Movie(**movie.dict())
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return new_movie

@app.get("/movies/", response_model=List[MovieSchema], tags=["Movies"])
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Movie).offset(skip).limit(limit).all()

# İzleme geçmişi
@app.post("/users/{user_id}/watch/{movie_id}", tags=["Watch History"])
def add_watch_history(user_id: int, movie_id: int, watch_data: WatchHistory, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Veritabanına ekle
    insert_stmt = watch_history.insert().values(
        user_id=user_id,
        movie_id=movie_id,
        rating=watch_data.rating
    )
    db.execute(insert_stmt)
    db.commit()

    return {"status": "success"}

# Öneriler
@app.get("/users/{user_id}/recommendations/", response_model=List[MovieSchema], tags=["Recommendations"])
def get_recommendations(user_id: int, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        watched_movies = pd.DataFrame([
            {
                'id': movie.id,
                'title': movie.title,
                'genre': movie.genre,
                'year': movie.year
            } for movie in user.watched_movies
        ])

        all_movies = pd.DataFrame([
            {
                'id': movie.id,
                'title': movie.title,
                'genre': movie.genre,
                'year': movie.year
            } for movie in db.query(Movie).all()
        ])

        if watched_movies.empty:
            raise HTTPException(status_code=400, detail="No watch history found")

        recommender.fit(all_movies)
        recommendations = recommender.get_recommendations(watched_movies, all_movies)

        if recommendations.empty:
            return []

        recommended_movies = db.query(Movie).filter(
            Movie.id.in_(recommendations['id'].tolist())
        ).all()

        return recommended_movies

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Veritabanı bağlantı testi
def test_db_connection():
    try:
        with engine.connect() as connection:
            print("Veritabanına başarıyla bağlanıldı!")
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"Mevcut Tablolar: {tables}")
    except Exception as e:
        print(f"Veritabanına bağlanırken hata oluştu: {e}")

#test_db_connection()
