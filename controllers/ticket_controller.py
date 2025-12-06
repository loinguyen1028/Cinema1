from services.ticket_service import TicketService

class TicketController:
    def __init__(self):
        self.service = TicketService()

    def get_movies_by_date(self, date_str, keyword="", genre="Tất cả"):
        return self.service.get_movies_by_date(date_str, keyword, genre)

    def get_detail(self, st_id):
        return self.service.get_showtime_detail(st_id)

    def get_products(self):
        return self.service.get_products()

    # --- Kiểm tra giảm giá thành viên ---
    def check_member_discount(self, phone):
        # Gọi hàm calculate_discount trong service
        # type_selection mặc định là "Thành viên" khi gọi hàm này
        return self.service.calculate_discount(phone, "Người lớn / Thành viên")

    # --- Lấy % giảm giá đặc biệt (Sinh viên/Trẻ em) ---
    def get_special_discount(self, customer_type):
        # Gọi service với sđt=None để chỉ lấy % special
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