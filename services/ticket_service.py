from dao.ticket_dao import TicketDAO
from dao.showtime_dao import ShowtimeDAO
from dao.customer_dao import CustomerDAO
from dao.product_dao import ProductDAO


class TicketService:
    def __init__(self):
        self.ticket_dao = TicketDAO()
        self.showtime_dao = ShowtimeDAO()
        self.customer_dao = CustomerDAO()
        self.product_dao = ProductDAO()

    # --- Lấy dữ liệu ---
    def get_movies_by_date(self, date_str, keyword="", genre="Tất cả"):
        all_showtimes = self.showtime_dao.filter_showtimes(date_str=date_str)
        grouped = {}
        for st in all_showtimes:
            m = st.movie
            # Filter keyword & genre logic here...
            if keyword and keyword.lower() not in m.title.lower(): continue
            m_genre = m.extra_info.get('genre', '') if m.extra_info else ""
            if genre != "Tất cả" and genre not in m_genre: continue

            if m.movie_id not in grouped:
                grouped[m.movie_id] = {'data': m, 'showtimes': []}
            grouped[m.movie_id]['showtimes'].append(st)
        return list(grouped.values())

    def get_showtime_detail(self, st_id):
        return self.showtime_dao.get_showtime_by_id(st_id)

    def get_products(self):
        return self.product_dao.get_all()

    def get_all_tickets(self):
        return self.ticket_dao.get_all_tickets()

    def search_tickets(self, kw):
        return self.ticket_dao.search_tickets(kw)

    # --- Logic Nghiệp vụ ---

    def calculate_discount(self, customer_phone, type_selection):
        """Tính toán giảm giá dựa trên SĐT và loại khách"""
        # 1. Giảm giá đặc biệt (Sinh viên/Trẻ em)
        special_rates = {"Sinh viên": 0.20, "Trẻ em": 0.30, "Người cao tuổi": 0.20}
        special_percent = special_rates.get(type_selection, 0.0)

        customer = None
        member_percent = 0.0
        msg = ""

        # 2. Check thành viên
        if customer_phone:
            customer = self.customer_dao.get_by_phone(customer_phone)
            if customer:
                extra = customer.extra_info if customer.extra_info else {}
                level = extra.get("level", "Thân thiết")
                mem_rates = {"Thân thiết": 0.05, "Bạc": 0.10, "Vàng": 0.15, "Kim cương": 0.20}
                member_percent = mem_rates.get(level, 0)
                msg = f"Thành viên: {customer.name} ({level})"
            else:
                msg = "Khách vãng lai"

        # Quyết định dùng giảm giá nào (Ưu tiên cái cao hơn hoặc cộng dồn tùy chính sách)
        # Ở đây ví dụ ưu tiên Special nếu có, không thì lấy Member
        final_percent = max(special_percent, member_percent)

        return customer, final_percent, msg

    def process_payment(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None, points_used=0,
                        products_list=None):
        """Xử lý giao dịch thanh toán vé trọn gói"""
        if not seat_ids:
            return False, "Vui lòng chọn ít nhất 1 ghế!"

        # 1. Trừ điểm (nếu có)
        if customer_id and points_used > 0:
            ok, msg_deduct = self.customer_dao.deduct_points(customer_id, points_used)
            if not ok: return False, msg_deduct

        # 2. Tạo vé
        success, msg = self.ticket_dao.create_ticket(
            showtime_id, user_id, seat_ids, total_amount,
            customer_id=customer_id,
            products_list=products_list
        )

        # 3. Cộng điểm tích lũy
        if success and customer_id:
            ok_add, point_msg = self.customer_dao.update_membership(customer_id, total_amount)
            if ok_add: msg += f"\n({point_msg})"
            if points_used > 0: msg += f"\n(Đã trừ {points_used} điểm)"

        return success, msg

    def cancel_ticket(self, ticket_id):
        # Có thể thêm logic: Không cho hủy nếu vé đã in hoặc phim đã chiếu
        return self.ticket_dao.delete_ticket(ticket_id)