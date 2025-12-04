from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base

class Room(Base):
    __tablename__ = 'rooms'
    
    room_id = Column(Integer, primary_key=True)
    room_name = Column(String(50), unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)

    # Quan hệ
    seats = relationship("Seat", back_populates="room", cascade="all, delete-orphan")
    showtimes = relationship("Showtime", back_populates="room")

    def __repr__(self):
        return f"<Room(name='{self.room_name}')>"

class Seat(Base):
    __tablename__ = 'seats'
    
    seat_id = Column(Integer, primary_key=True)
    room_id = Column(Integer, ForeignKey('rooms.room_id', ondelete='CASCADE'), nullable=False)
    seat_row = Column(String(5), nullable=False)
    seat_number = Column(Integer, nullable=False)

    # Quan hệ
    room = relationship("Room", back_populates="seats")
    
    # Ràng buộc duy nhất (1 ghế không thể trùng hàng/số trong cùng 1 phòng)
    __table_args__ = (UniqueConstraint('room_id', 'seat_row', 'seat_number', name='uix_room_seat'),)

    def __repr__(self):
        return f"<Seat({self.seat_row}{self.seat_number})>"