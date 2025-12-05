from dao.showtime_dao import ShowtimeDAO
from datetime import datetime
from dao.ticket_dao import TicketDAO
from dao.customer_dao import CustomerDAO

class TicketController:
    def __init__(self):
        self.dao = ShowtimeDAO()
        self.ticket_dao = TicketDAO()
        self.customer_dao = CustomerDAO()

    def get_movies_by_date(self, date_str, keyword="", genre="Tất cả"):
        """
        Lấy danh sách phim có suất chiếu trong ngày date_str.
        Hỗ trợ lọc theo keyword (tên phim) và genre (thể loại).
        """
        # 1. Lấy tất cả suất chiếu trong ngày đó
        # (Gọi hàm filter_showtimes của DAO đã viết ở bài trước)
        all_showtimes = self.dao.filter_showtimes(date_str=date_str)

        # 2. Gom nhóm suất chiếu theo Phim
        # Cấu trúc: { movie_id: { 'movie_obj': movie, 'showtimes': [st1, st2...] } }
        grouped_movies = {}

        for st in all_showtimes:
            m = st.movie

            # --- BỘ LỌC (Filter) ---
            # 1. Lọc tên phim
            if keyword and keyword.lower() not in m.title.lower():
                continue

            # 2. Lọc thể loại
            # Lấy genre từ JSON extra_info
            m_genre = ""
            if m.extra_info and 'genre' in m.extra_info:
                m_genre = m.extra_info['genre']

            if genre != "Tất cả" and genre not in m_genre:
                continue
            # -----------------------

            # Gom nhóm
            if m.movie_id not in grouped_movies:
                grouped_movies[m.movie_id] = {
                    'data': m,
                    'showtimes': []
                }

            grouped_movies[m.movie_id]['showtimes'].append(st)

        # Trả về danh sách các values (bỏ key id)
        return list(grouped_movies.values())

    def get_detail(self, st_id):
        return self.dao.get_showtime_by_id(st_id)

    def get_special_discount(self, customer_type):
        """Trả về % giảm giá cho các đối tượng đặc biệt"""
        rates = {
            "Sinh viên": 0.20,  # Giảm 20%
            "Trẻ em": 0.30,  # Giảm 30%
            "Người cao tuổi": 0.20  # Thêm nếu muốn
        }
        return rates.get(customer_type, 0.0)

    def check_member_discount(self, phone):
        """
        Kiểm tra khách hàng và trả về mức giảm giá.
        Return: (Customer Object, Discount Percent, Message)
        """
        customer = self.customer_dao.get_by_phone(phone)

        if not customer:
            return None, 0, "Khách hàng không tồn tại (Khách vãng lai)"

        # Lấy level từ JSON
        extra = customer.extra_info if customer.extra_info else {}
        level = extra.get("level", "Thân thiết")

        # BẢNG TỶ LỆ GIẢM GIÁ (Bạn có thể sửa tùy ý)
        discount_map = {
            "Thân thiết": 0.05,  # 5%
            "Bạc": 0.10,  # 10%
            "Vàng": 0.15,  # 15%
            "Kim cương": 0.20  # 20%
        }

        percent = discount_map.get(level, 0)
        return customer, percent, f"Khách: {customer.name} - Hạng: {level} (Giảm {int(percent * 100)}%)"

    def process_payment(self, showtime_id, user_id, seat_ids, total_amount, customer_id=None):
        if not seat_ids:
            return False, "Vui lòng chọn ít nhất 1 ghế!"

            # 1. Tạo vé trước
        success, msg = self.ticket_dao.create_ticket(showtime_id, user_id, seat_ids, total_amount, customer_id)

        # 2. Nếu tạo vé thành công VÀ có khách hàng -> Tích điểm
        if success and customer_id:
            # Gọi DAO để cộng điểm
            ok, point_msg = self.customer_dao.update_membership(customer_id, total_amount)
            if ok:
                msg += f"\n\n({point_msg})"  # Nối thêm thông báo tích điểm

        return success, msg