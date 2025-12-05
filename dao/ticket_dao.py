from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import Ticket, TicketSeat
from datetime import datetime


class TicketDAO:
    def create_ticket(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None):
        session = db.get_session()
        try:
            # 1. Tạo đối tượng Ticket (Hóa đơn)
            new_ticket = Ticket(
                showtime_id=showtime_id,
                user_id=user_id,  # ID nhân viên bán
                customer_id=customer_id,  # Có thể None nếu khách vãng lai
                total_amount=total_amount,
                booking_time=datetime.now()
            )
            session.add(new_ticket)
            session.flush()  # Đẩy lên để lấy ticket_id về (chưa commit)

            # 2. Tạo chi tiết ghế (TicketSeat)
            # Giả sử giá vé lấy từ suất chiếu, nhưng ở đây ta lưu giá thực tế bán
            unit_price = total_amount / len(seat_ids) if seat_ids else 0

            for s_id in seat_ids:
                ts = TicketSeat(
                    ticket_id=new_ticket.ticket_id,
                    seat_id=s_id,
                    price=unit_price
                )
                session.add(ts)

            # 3. Commit tất cả
            session.commit()
            return True, f"Thanh toán thành công! Mã vé: {new_ticket.ticket_id}"
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Lỗi thanh toán: {e}")
            return False, "Lỗi khi lưu vào Database"
        finally:
            session.close()