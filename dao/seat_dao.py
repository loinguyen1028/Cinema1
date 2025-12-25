from db import db
from models import Seat, TicketSeat, Ticket
from sqlalchemy import func


class SeatDAO:
    def get_seats_by_room(self, room_id):
        session = db.get_session()
        try:
            return session.query(Seat) \
                .filter_by(room_id=room_id) \
                .order_by(Seat.seat_row, Seat.seat_number) \
                .all()
        finally:
            session.close()

    def get_booked_seat_ids(self, showtime_id):
        session = db.get_session()
        try:
            booked = session.query(TicketSeat.seat_id) \
                .join(Ticket) \
                .filter(
                    Ticket.showtime_id == showtime_id,
                    Ticket.status == 'booked'
                ).all()
            return [b[0] for b in booked]
        finally:
            session.close()
