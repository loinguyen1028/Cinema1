from sqlalchemy.exc import SQLAlchemyError
# --- SỬA LỖI: Import joinedload ---
from sqlalchemy.orm import joinedload
from db import db
# --- SỬA LỖI: Import đầy đủ các Model cần dùng để Join ---
from models import Ticket, TicketSeat, TicketProduct, Showtime, Movie, Room, Customer, User
from datetime import datetime


class TicketDAO:
    # ---------------------------------------------------------
    # TẠO VÉ (BÁN VÉ)
    # ---------------------------------------------------------
    def create_ticket(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None, products_list=None):
        session = db.get_session()
        try:
            # 1. Tạo Ticket
            new_ticket = Ticket(
                showtime_id=showtime_id,
                user_id=user_id,
                customer_id=customer_id,
                total_amount=total_amount,
                booking_time=datetime.now()
            )
            session.add(new_ticket)
            session.flush()

            # 2. Lưu ghế (Nếu có)
            if showtime_id:
                st = session.query(Showtime).get(showtime_id)
                unit_price = st.ticket_price if st else 0
            else:
                unit_price = 0  # Trường hợp bán bắp nước riêng

            for s_id in seat_ids:
                ts = TicketSeat(
                    ticket_id=new_ticket.ticket_id,
                    seat_id=s_id,
                    price=unit_price
                )
                session.add(ts)

            # 3. Lưu sản phẩm (Nếu có)
            if products_list:
                for p_id, qty, price in products_list:
                    tp = TicketProduct(
                        ticket_id=new_ticket.ticket_id,
                        product_id=p_id,
                        quantity=qty,
                        price_at_purchase=price
                    )
                    session.add(tp)

            session.commit()
            return True, f"Thanh toán thành công! Mã vé: {new_ticket.ticket_id}"

        except SQLAlchemyError as e:
            session.rollback()
            print(f"Lỗi thanh toán: {e}")
            return False, "Lỗi khi lưu vào Database"
        finally:
            session.close()

    # ---------------------------------------------------------
    # QUẢN LÝ VÉ (XEM / TÌM / HỦY)
    # ---------------------------------------------------------
    def get_all_tickets(self):
        """Lấy danh sách tất cả vé, kèm thông tin chi tiết"""
        session = db.get_session()
        try:
            # Join với Customer, Showtime, Movie, Room... để lấy đủ info hiển thị
            return session.query(Ticket).options(
                joinedload(Ticket.customer),
                joinedload(Ticket.user),
                joinedload(Ticket.showtime).joinedload(Showtime.movie),
                joinedload(Ticket.showtime).joinedload(Showtime.room),
                joinedload(Ticket.ticket_seats).joinedload(TicketSeat.seat)
            ).order_by(Ticket.ticket_id.desc()).all()
        finally:
            session.close()

    def search_tickets(self, keyword):
        """Tìm kiếm theo ID vé hoặc SĐT khách"""
        session = db.get_session()
        try:
            # SỬA LỖI: Thêm joinedload(Showtime.room) vào options
            query = session.query(Ticket).options(
                joinedload(Ticket.customer),
                joinedload(Ticket.user),  # Thêm user nếu cần
                joinedload(Ticket.showtime).joinedload(Showtime.movie),
                joinedload(Ticket.showtime).joinedload(Showtime.room),  # <--- QUAN TRỌNG: Phải load Room ở đây
                joinedload(Ticket.ticket_seats).joinedload(TicketSeat.seat)
            ).join(Customer, isouter=True)

            if keyword.isdigit():
                query = query.filter((Ticket.ticket_id == int(keyword)) | (Customer.phone.ilike(f"%{keyword}%")))
            else:
                query = query.filter(Customer.name.ilike(f"%{keyword}%"))

            return query.order_by(Ticket.ticket_id.desc()).all()
        except Exception as e:
            print(f"Lỗi search ticket: {e}")
            return []
        finally:
            session.close()

    def delete_ticket(self, ticket_id):
        """Hủy vé (Xóa khỏi DB -> Ghế sẽ trống lại)"""
        session = db.get_session()
        try:
            ticket = session.query(Ticket).get(ticket_id)
            if ticket:
                session.delete(ticket)
                session.commit()
                return True, "Hủy vé thành công!"
            return False, "Không tìm thấy vé"
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()