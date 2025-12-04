from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base

class Movie(Base):
    __tablename__ = 'movies'
    movie_id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    duration_min = Column(Integer, nullable=False)
    rating = Column(String(10))
    description = Column(Text)
    poster_path = Column(String(255))
    extra_info = Column(JSONB)

    showtimes = relationship("Showtime", back_populates="movie")

class Showtime(Base):
    __tablename__ = 'showtimes'
    showtime_id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.movie_id'), nullable=False)
    room_id = Column(Integer, ForeignKey('rooms.room_id'), nullable=False)
    start_time = Column(DateTime, nullable=False)
    ticket_price = Column(Numeric(10, 2), nullable=False)
    extra_info = Column(JSONB)

    movie = relationship("Movie", back_populates="showtimes")
    room = relationship("Room", back_populates="showtimes")
    tickets = relationship("Ticket", back_populates="showtime")