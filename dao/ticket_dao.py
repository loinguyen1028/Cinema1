from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from db import db
# Nhớ import Customer để truy vấn thông tin khách
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
                status='booked'
            )
            session.add(new_ticket)
            session.flush()

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

            if products_list:
                for p_id, qty, price in products_list:
                    tp = TicketProduct(
                        ticket_id=new_ticket.ticket_id,
                        product_id=p_id,
                        quantity=qty,
                        price_at_purchase=price
                    )
                    session.add(tp)

            if customer_id:
                cus = session.query(Customer).get(customer_id)
                if cus:
                    points_added = int(total_amount / 1000)


                    current_info = dict(cus.extra_info) if cus.extra_info else {}
                    current_points = current_info.get("points", 0)


                    new_points = current_points + points_added


                    new_level = "Thân thiết"
                    if new_points >= 5000:
                        new_level = "Kim cương"
                    elif new_points >= 2000:
                        new_level = "Vàng"
                    elif new_points >= 1000:
                        new_level = "Bạc"


                    current_info["points"] = new_points
                    current_info["level"] = new_level
                    cus.extra_info = current_info


                    print(
                        f"--- Đã cộng {points_added} điểm cho khách {cus.name}. Tổng: {new_points}. Hạng: {new_level} ---")
            # =========================================================

            session.commit()
            return True, f"Thanh toán thành công! Mã vé: {new_ticket.ticket_id}"

        except SQLAlchemyError as e:
            session.rollback()
            print(f"Lỗi thanh toán: {e}")
            return False, "Lỗi khi lưu vào Database"
        finally:
            session.close()


    def create_concession_transaction(self, user_id, total_amount, products_list, customer_id=None):
        session = db.get_session()
        try:

            new_ticket = Ticket(
                user_id=user_id,
                customer_id=customer_id,
                showtime_id=None,
                booking_time=datetime.now(),
                total_amount=total_amount,
                status='booked',
            )
            session.add(new_ticket)
            session.flush()


            for pid, qty, price in products_list:
                tp = TicketProduct(
                    ticket_id=new_ticket.ticket_id,
                    product_id=pid,
                    quantity=qty,
                    price_at_purchase=price
                )
                session.add(tp)


            if customer_id:

                cus = session.query(Customer).get(customer_id)
                if cus:

                    points_added = int(total_amount / 1000)


                    current_info = dict(cus.extra_info) if cus.extra_info else {}
                    current_points = current_info.get("points", 0)


                    new_points = current_points + points_added


                    new_level = "Thân thiết"
                    if new_points >= 5000:
                        new_level = "Kim cương"
                    elif new_points >= 2000:
                        new_level = "Vàng"
                    elif new_points >= 1000:
                        new_level = "Bạc"


                    current_info["points"] = new_points
                    current_info["level"] = new_level
                    cus.extra_info = current_info
                    print(f"--- Đã cộng {points_added} điểm. Tổng: {new_points}. Hạng: {new_level} ---")


            session.commit()
            return True, f"Thanh toán thành công! Mã vé: {new_ticket.ticket_id}"

        except Exception as e:
            session.rollback()
            print(f"Lỗi tạo hóa đơn bắp nước: {e}")
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()


    def get_all_tickets(self):
        session = db.get_session()
        try:
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
        session = db.get_session()
        try:
            ticket = session.query(Ticket).get(ticket_id)
            if ticket:
                ticket.status = 'cancelled'
                for ts in ticket.ticket_seats:
                    session.delete(ts)
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