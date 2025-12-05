from dao.showtime_dao import ShowtimeDAO
from datetime import datetime


class ShowtimeController:
    def __init__(self):
        self.dao = ShowtimeDAO()

    def get_list(self, date_filter=None, room_filter=None):
        return self.dao.filter_showtimes(date_filter, room_filter)

    def get_detail(self, st_id):
        return self.dao.get_showtime_by_id(st_id)

    def delete(self, st_id):
        if self.dao.delete_showtime(st_id):
            return True, "Xóa thành công"
        return False, "Lỗi xóa dữ liệu"

    def get_resources(self):
        """Lấy danh sách phim và phòng để điền vào Combobox"""
        movies = self.dao.get_movies_list()
        rooms = self.dao.get_rooms_list()
        return movies, rooms

    def save(self, mode, st_id, movie_id, room_id, date_str, time_str, price):
        # 1. Validate
        if not movie_id or not room_id:
            return False, "Vui lòng chọn Phim và Phòng chiếu"
        if not date_str or not time_str:
            return False, "Vui lòng nhập Ngày và Giờ chiếu"

        # 2. Gộp Ngày + Giờ thành datetime object
        try:
            full_str = f"{date_str} {time_str}"
            start_dt = datetime.strptime(full_str, "%d/%m/%Y %H:%M")
        except ValueError:
            return False, "Định dạng ngày (dd/mm/yyyy) hoặc giờ (HH:MM) không hợp lệ"

        if not str(price).isdigit():
            return False, "Giá vé phải là số"

        # 3. Gọi DAO
        if mode == "add":
            success = self.dao.add_showtime(movie_id, room_id, start_dt, float(price))
        else:
            success = self.dao.update_showtime(st_id, movie_id, room_id, start_dt, float(price))

        return (True, "Thành công") if success else (False, "Lỗi Database")