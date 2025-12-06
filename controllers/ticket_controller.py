from dao.showtime_dao import ShowtimeDAO
from dao.ticket_dao import TicketDAO
from dao.customer_dao import CustomerDAO
from dao.product_dao import ProductDAO  # <--- QUAN TRỌNG: Đã thêm dòng này
from datetime import datetime


class TicketController:
    def __init__(self):
        self.showtime_dao = ShowtimeDAO()
        self.ticket_dao = TicketDAO()
        self.customer_dao = CustomerDAO()
        self.product_dao = ProductDAO()  # Khởi tạo ProductDAO

    def get_movies_by_date(self, date_str, keyword="", genre="Tất cả"):
        """
        Lấy danh sách phim có suất chiếu trong ngày date_str.
        """
        all_showtimes = self.showtime_dao.filter_showtimes(date_str=date_str)
        grouped_movies = {}

        for st in all_showtimes:
            m = st.movie

            # Filter keyword
            if keyword and keyword.lower() not in m.title.lower():
                continue

            # Filter genre
            m_genre = ""
            if m.extra_info and 'genre' in m.extra_info:
                m_genre = m.extra_info['genre']

            if genre != "Tất cả" and genre not in m_genre:
                continue

            if m.movie_id not in grouped_movies:
                grouped_movies[m.movie_id] = {
                    'data': m,
                    'showtimes': []
                }

            grouped_movies[m.movie_id]['showtimes'].append(st)

        return list(grouped_movies.values())

    def get_detail(self, st_id):
        return self.showtime_dao.get_showtime_by_id(st_id)

    # --- HÀM LẤY % GIẢM GIÁ ĐẶC BIỆT ---
    def get_special_discount(self, customer_type):
        rates = {
            "Sinh viên": 0.20,  # 20%
            "Trẻ em": 0.30,  # 30%
            "Người cao tuổi": 0.20
        }
        return rates.get(customer_type, 0.0)

    # --- HÀM KIỂM TRA THÀNH VIÊN ---
    def check_member_discount(self, phone):
        customer = self.customer_dao.get_by_phone(phone)
        if not customer:
            return None, 0, "Khách vãng lai"

        extra = customer.extra_info if customer.extra_info else {}
        level = extra.get("level", "Thân thiết")

        discount_map = {
            "Thân thiết": 0.05,
            "Bạc": 0.10,
            "Vàng": 0.15,
            "Kim cương": 0.20
        }
        percent = discount_map.get(level, 0)
        return customer, percent, f"Thành viên: {customer.name} ({level})"

    # --- HÀM LẤY DANH SÁCH SẢN PHẨM ---
    def get_products(self):
        return self.product_dao.get_all()

    # --- HÀM XỬ LÝ THANH TOÁN (FULL) ---
    def process_payment(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None, points_used=0,
                        products_list=None):
        if not seat_ids:
            return False, "Vui lòng chọn ít nhất 1 ghế!"

        # 1. Trừ điểm (Nếu có dùng)
        if customer_id and points_used > 0:
            ok, msg_deduct = self.customer_dao.deduct_points(customer_id, points_used)
            if not ok:
                return False, msg_deduct  # Dừng nếu không đủ điểm

        # 2. Tạo vé (Kèm sản phẩm nếu có)
        success, msg = self.ticket_dao.create_ticket(
            showtime_id, user_id, seat_ids, total_amount,
            customer_id=customer_id,
            products_list=products_list
        )

        # 3. Cộng điểm (Nếu thành công)
        if success and customer_id:
            # Chỉ tích điểm trên số tiền thực trả (total_amount)
            ok_add, point_msg = self.customer_dao.update_membership(customer_id, total_amount)
            if ok_add:
                msg += f"\n\n({point_msg})"

            if points_used > 0:
                msg += f"\n(Đã dùng {points_used} điểm)"

        return success, msg

    def get_all_tickets(self):
        return self.ticket_dao.get_all_tickets()

    def search_tickets(self, keyword):
        if not keyword:
            return self.get_all_tickets()
        return self.ticket_dao.search_tickets(keyword)

    def cancel_ticket(self, ticket_id):
        # Có thể thêm logic kiểm tra: Chỉ cho hủy trước giờ chiếu bao lâu đó
        return self.ticket_dao.delete_ticket(ticket_id)