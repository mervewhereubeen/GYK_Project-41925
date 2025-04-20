from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from .database import Base

# Kullanıcı-Film izleme geçmişi için ara tablo
watch_history = Table(
    'watch_history',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('movie_id', Integer, ForeignKey('movies.id'), primary_key=True),
    Column('rating', Float)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    
    # İlişkiler
    watched_movies = relationship(
        "Movie",
        secondary=watch_history,
        back_populates="watched_by"
    )

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    genre = Column(String)
    year = Column(Integer)
    
    # İlişkiler
    watched_by = relationship(
        "User",
        secondary=watch_history,
        back_populates="watched_movies"
    )
