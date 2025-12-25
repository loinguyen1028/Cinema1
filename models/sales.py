from sqlalchemy import Column, Integer, String, DateTime, Numeric, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from .base import Base


class MembershipTier(Base):
    __tablename__ = 'membership_tiers'
    id = Column(Integer, primary_key=True)
    tier_name = Column(String(50), nullable=False)
    min_point = Column(Integer, default=0)
    discount_percent = Column(Numeric(5, 2), default=0)

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True)
    email = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)


    points = Column(Integer, default=0)
    tier_id = Column(Integer, ForeignKey('membership_tiers.id'))


    extra_info = Column(JSONB)
    is_active = Column(Boolean, default=True)


    tier = relationship("MembershipTier")
    tickets = relationship("Ticket", back_populates="customer")


class Ticket(Base):
    __tablename__ = 'tickets'
    ticket_id = Column(Integer, primary_key=True)
    showtime_id = Column(Integer, ForeignKey('showtimes.showtime_id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.customer_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    booking_time = Column(DateTime, default=datetime.now)
    total_amount = Column(Numeric(10, 2), nullable=False)
    payment_info = Column(JSONB)

    showtime = relationship("Showtime", back_populates="tickets")
    customer = relationship("Customer", back_populates="tickets")
    user = relationship("User", back_populates="sales")
    status = Column(String(20), default='booked')


    ticket_seats = relationship("TicketSeat", back_populates="ticket", cascade="all, delete-orphan")


    ticket_products = relationship("TicketProduct", back_populates="ticket", cascade="all, delete-orphan")


class TicketSeat(Base):
    __tablename__ = 'ticket_seats'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.ticket_id', ondelete='CASCADE'), nullable=False)
    seat_id = Column(Integer, ForeignKey('seats.seat_id'), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)

    ticket = relationship("Ticket", back_populates="ticket_seats")
    seat = relationship("Seat")


    __table_args__ = (UniqueConstraint('ticket_id', 'seat_id', name='uix_ticket_seat'),)


class TicketProduct(Base):
    __tablename__ = 'ticket_products'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.ticket_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price_at_purchase = Column(Numeric(10, 2), nullable=False)

    ticket = relationship("Ticket", back_populates="ticket_products")
    product = relationship("Product", back_populates="ticket_products")