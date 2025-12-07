from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from db import db
from models import Ticket, TicketSeat, TicketProduct, Showtime, Movie, Room, Customer, User
from datetime import datetime


class TicketDAO:
    def create_ticket(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None, products_list=None):
        session = db.get_session()
        try:
            # 1. Tạo Ticket
            new_ticket = Ticket(
                showtime_id=showtime_id,
                user_id=user_id,
                customer_id=customer_id,
                total_amount=total_amount,
                booking_time=datetime.now(),
                status='booked'  # Mặc định là đã đặt
            )
            session.add(new_ticket)
            session.flush()

            # 2. Lưu ghế (Nếu có)
            if showtime_id:
                st = session.query(Showtime).get(showtime_id)
                unit_price = st.ticket_price if st else 0
            else:
                unit_price = 0

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
        """Lấy danh sách vé (Chỉ lấy vé trạng thái 'booked')"""
        session = db.get_session()
        try:
            # --- SỬA LỖI TẠI ĐÂY: Thay dấu ... bằng code đầy đủ ---
            return session.query(Ticket).options(
                joinedload(Ticket.customer),
                joinedload(Ticket.user),
                joinedload(Ticket.showtime).joinedload(Showtime.movie),
                joinedload(Ticket.showtime).joinedload(Showtime.room),
                joinedload(Ticket.ticket_seats).joinedload(TicketSeat.seat)
            ).filter(Ticket.status == 'booked').order_by(Ticket.ticket_id.desc()).all()
        finally:
            session.close()

    def search_tickets(self, keyword):
        """Tìm kiếm vé (Chỉ tìm vé 'booked')"""
        session = db.get_session()
        try:
            query = session.query(Ticket).options(
                joinedload(Ticket.customer),
                joinedload(Ticket.user),
                joinedload(Ticket.showtime).joinedload(Showtime.movie),
                joinedload(Ticket.showtime).joinedload(Showtime.room),
                joinedload(Ticket.ticket_seats).joinedload(TicketSeat.seat)
            ).join(Customer, isouter=True).filter(Ticket.status == 'booked')

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
        """Hủy vé (Soft Delete: Đổi trạng thái -> booked thành cancelled)"""
        session = db.get_session()
        try:
            ticket = session.query(Ticket).get(ticket_id)
            if ticket:
                # 1. Đổi trạng thái vé
                ticket.status = 'cancelled'

                # 2. Xóa ghế để nhả chỗ cho người khác mua
                # (Xóa cứng trong bảng ticket_seats, nhưng vé cha vẫn còn để lưu lịch sử)
                for ts in ticket.ticket_seats:
                    session.delete(ts)

                # 3. Xóa liên kết sản phẩm (nếu muốn hoàn kho hoặc hủy đơn bắp nước)
                # Tùy nghiệp vụ, ở đây ta xóa luôn cho gọn
                for tp in ticket.ticket_products:
                    session.delete(tp)

                session.commit()
                return True, "Đã hủy vé thành công!"
            return False, "Không tìm thấy vé"
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()

    def create_concession_transaction(self, user_id, total_amount, products_list, customer_id=None):
        """
        Tạo hóa đơn chỉ có bắp nước (không có suất chiếu/ghế)
        """
        session = db.get_session()
        try:
            # 1. Tạo Ticket (Hóa đơn)
            # Lưu ý: showtime_id để NULL (None)
            new_ticket = Ticket(
                user_id=user_id,
                customer_id=customer_id,
                showtime_id=None,  # Quan trọng: Không gắn với suất chiếu
                booking_time=datetime.now(),
                total_amount=total_amount
            )
            session.add(new_ticket)
            session.flush()  # Để lấy ticket_id

            # 2. Lưu chi tiết sản phẩm (TicketProduct)
            for pid, qty, price in products_list:
                tp = TicketProduct(
                    ticket_id=new_ticket.ticket_id,
                    product_id=pid,
                    quantity=qty,
                    price_at_purchase=price
                )
                session.add(tp)

            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Lỗi tạo hóa đơn bắp nước: {e}")
            return False
        finally:
            session.close()