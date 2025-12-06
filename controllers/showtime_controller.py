from services.showtime_service import ShowtimeService


class ShowtimeController:
    def __init__(self):
        self.service = ShowtimeService()

    def get_list(self, date_filter=None, room_filter=None):
        return self.service.get_list(date_filter, room_filter)

    def get_detail(self, st_id):
        return self.service.get_detail(st_id)

    def get_resources(self):
        # Hàm này vẫn cần gọi DAO trực tiếp hoặc thêm vào Service nếu muốn
        # Nhưng để nhanh, ta có thể dùng service của Room và Movie đã có
        # Tuy nhiên, ở đây ta để tạm việc gọi DAO bên trong service showtime
        # (Bạn cần bổ sung hàm get_movies_list, get_rooms_list vào ShowtimeService nếu muốn triệt để)
        # Giả sử ta lấy trực tiếp từ các service khác hoặc service này tự handle
        from services.movie_service import MovieService
        from services.room_service import RoomService

        movies = MovieService().get_all_movies()
        rooms = RoomService().get_all()

        # --- SỬA LỖI TẠI ĐÂY ---
        # Trả về trực tiếp list object (để View có thể gọi .title, .room_name)
        # Thay vì trả về list tuple [(id, name)] gây lỗi AttributeError
        return movies, rooms

    def save(self, mode, st_id, movie_id, room_id, date_str, time_str, price):
        return self.service.save_showtime(mode, st_id, movie_id, room_id, date_str, time_str, price)

    def delete(self, st_id):
        return self.service.delete_showtime(st_id)