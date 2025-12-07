from dao.showtime_dao import ShowtimeDAO
from datetime import datetime
from dao.movie_dao import MovieDAO # Import thêm để lấy thời lượng phim
from datetime import datetime, timedelta

class ShowtimeService:
    def __init__(self):
        self.dao = ShowtimeDAO()
        self.movie_dao = MovieDAO()

    def get_list(self, date_filter=None, room_filter=None):
        return self.dao.filter_showtimes(date_filter, room_filter)

    def get_detail(self, st_id):
        return self.dao.get_showtime_by_id(st_id)

    def save_showtime(self, mode, st_id, movie_id, room_id, date_str, time_str, price):
        # 1. Validate dữ liệu đầu vào
        if not movie_id or not room_id:
            return False, "Chưa chọn Phim hoặc Phòng"

        try:
            full_str = f"{date_str} {time_str}"
            new_start = datetime.strptime(full_str, "%d/%m/%Y %H:%M")
        except ValueError:
            return False, "Định dạng Ngày/Giờ không đúng"

        try:
            price_val = float(price)
            if price_val < 0:
                return False, "Giá vé không được nhỏ hơn 0"
        except ValueError:
            return False, "Giá vé phải là số (không được chứa chữ cái)"

        # 2. (Nâng cao) Có thể thêm logic check trùng lịch chiếu tại đây
        # existing = self.dao.check_conflict(room_id, start_dt, duration) ...

        # A. Lấy thông tin phim để biết thời lượng
        movie = self.movie_dao.get_movie_by_id(movie_id)
        if not movie:
            return False, "Phim không tồn tại!"

        duration = movie.duration_min

        # B. Tính giờ kết thúc dự kiến
        # Công thức: Giờ chiếu + Thời lượng phim + 15 phút dọn rạp
        cleaning_time = 15
        new_end = new_start + timedelta(minutes=duration + cleaning_time)

        # C. Lấy danh sách các suất chiếu ĐÃ CÓ trong phòng đó, ngày đó
        existing_showtimes = self.dao.get_showtimes_by_room_date(room_id, new_start.date())

        # D. Duyệt qua từng suất chiếu cũ để so sánh
        for st in existing_showtimes:
            # Nếu đang ở chế độ 'edit', bỏ qua chính suất chiếu đang sửa (tránh tự so sánh với mình)
            if mode == 'edit' and str(st.showtime_id) == str(st_id):
                continue

            # Tính giờ kết thúc của suất chiếu cũ
            st_end = st.start_time + timedelta(minutes=st.movie.duration_min + cleaning_time)

            # E. KIỂM TRA VA CHẠM (OVERLAP)
            # Logic: (StartA < EndB) và (StartB < EndA)
            if (new_start < st_end) and (st.start_time < new_end):
                conflict_time = st.start_time.strftime("%H:%M")
                conflict_end = st_end.strftime("%H:%M")
                return False, f"Trùng lịch! Phòng này đang chiếu phim '{st.movie.title}' ({conflict_time} - {conflict_end})"

        # 3. Gọi DAO
        if mode == "add":
            success = self.dao.add_showtime(movie_id, room_id, new_start, float(price))
        else:
            success = self.dao.update_showtime(st_id, movie_id, room_id, new_start, float(price))

        return (True, "Thành công") if success else (False, "Lỗi Database")

    def delete_showtime(self, st_id):
        if self.dao.delete_showtime(st_id):
            return True, "Xóa thành công"
        return False, "Lỗi khi xóa"