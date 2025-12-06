from db import db
from models import Seat, TicketSeat, Ticket, Showtime
from sqlalchemy import func

class SeatDAO:
    def get_seats_by_room(self, room_id):
        """Lấy tất cả ghế của phòng này, sắp xếp theo hàng và số"""
        session = db.get_session()
        try:
            return session.query(Seat).filter_by(room_id=room_id).order_by(Seat.seat_row, Seat.seat_number).all()
        finally:
            session.close()

    def get_booked_seat_ids(self, showtime_id):
        session = db.get_session()
        try:
            # Query: Chỉ lấy ghế của những vé có status = 'booked'
            booked = session.query(TicketSeat.seat_id) \
                .join(Ticket) \
                .filter(Ticket.showtime_id == showtime_id) \
                .filter(Ticket.status == 'booked') \
                .all()
            return [b[0] for b in booked]
        finally:
            session.close()