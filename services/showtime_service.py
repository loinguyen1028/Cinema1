from dao.showtime_dao import ShowtimeDAO
from datetime import datetime


class ShowtimeService:
    def __init__(self):
        self.dao = ShowtimeDAO()

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
            start_dt = datetime.strptime(full_str, "%d/%m/%Y %H:%M")
        except ValueError:
            return False, "Định dạng Ngày/Giờ không đúng"

        if not str(price).isdigit() or float(price) < 0:
            return False, "Giá vé không hợp lệ"

        # 2. (Nâng cao) Có thể thêm logic check trùng lịch chiếu tại đây
        # existing = self.dao.check_conflict(room_id, start_dt, duration) ...

        # 3. Gọi DAO
        if mode == "add":
            success = self.dao.add_showtime(movie_id, room_id, start_dt, float(price))
        else:
            success = self.dao.update_showtime(st_id, movie_id, room_id, start_dt, float(price))

        return (True, "Thành công") if success else (False, "Lỗi Database")

    def delete_showtime(self, st_id):
        if self.dao.delete_showtime(st_id):
            return True, "Xóa thành công"
        return False, "Lỗi khi xóa"