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
        """Lấy danh sách ID các ghế đã được đặt cho suất chiếu này"""
        session = db.get_session()
        try:
            # Query: Tìm seat_id trong bảng TicketSeat -> Ticket -> Showtime
            # ticket_seats JOIN tickets ON ... WHERE tickets.showtime_id = ...
            booked = session.query(TicketSeat.seat_id)\
                            .join(Ticket)\
                            .filter(Ticket.showtime_id == showtime_id).all()
            # Kết quả trả về là list các tuple [(1,), (2,), ...], cần chuyển về list [1, 2, ...]
            return [b[0] for b in booked]
        except Exception as e:
            print(f"Lỗi lấy ghế đã đặt: {e}")
            return []
        finally:
            session.close()