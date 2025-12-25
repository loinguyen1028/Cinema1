from services.ticket_service import TicketService
from models import User
from db import db

class TicketController:
    def __init__(self):
        self.service = TicketService()

    def get_movies_by_date(self, date_str, keyword="", genre="Tất cả"):
        return self.service.get_movies_by_date(date_str, keyword, genre)

    def get_detail(self, st_id):
        return self.service.get_showtime_detail(st_id)

    def get_products(self):
        return self.service.get_products()


    def check_member_discount(self, phone):

        return self.service.calculate_discount(phone, "Người lớn / Thành viên")


    def get_special_discount(self, customer_type):

        _, percent, _ = self.service.calculate_discount(None, customer_type)
        return percent

    def process_payment(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None, points_used=0, products_list=None):
        return self.service.process_payment(showtime_id, user_id, seat_ids, total_amount, customer_id, points_used, products_list)

    def get_all_tickets(self):
        return self.service.get_all_tickets()

    def search_tickets(self, keyword):
        return self.service.search_tickets(keyword)

    def cancel_ticket(self, ticket_id):
        return self.service.cancel_ticket(ticket_id)

    def get_user_name(self, user_id):
        """Lấy tên nhân viên bán vé theo ID"""
        if not user_id:
            return "Unknown"

        session = db.get_session()
        try:
            user = session.query(User).get(user_id)
            return user.username if user else "Unknown"
        except Exception as e:
            print(f"Lỗi lấy tên user: {e}")
            return "Error"
        finally:
            session.close()