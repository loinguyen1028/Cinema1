from dao.movie_dao import MovieDAO


class MovieService:
    def __init__(self):
        self.movie_dao = MovieDAO()

    def get_all_movies(self):
        return self.movie_dao.get_all_movies()

    def search_movies(self, keyword):
        if not keyword:
            return self.get_all_movies()
        return self.movie_dao.search_movies(keyword)

    def get_movie_by_id(self, movie_id):
        return self.movie_dao.get_movie_by_id(movie_id)

    def delete_movie(self, movie_id):
        # Có thể thêm logic kiểm tra: Nếu phim đang có suất chiếu thì không cho xóa
        if self.movie_dao.delete_movie(movie_id):
            return True, "Xóa phim thành công!"
        return False, "Lỗi: Không thể xóa phim này (có thể do ràng buộc dữ liệu)."

    def save_movie(self, mode, movie_id, name, duration, country, genre, actors, lang, age, desc, poster):
        """
        Hàm xử lý chung cho cả Thêm và Sửa
        Trả về: (Success: bool, Message: str)
        """
        # 1. VALIDATE DỮ LIỆU (Logic kiểm tra nằm hết ở đây)
        name = name.strip()
        duration = duration.strip()

        if not name:
            return False, "Vui lòng nhập tên phim!"

        if not duration:
            return False, "Vui lòng nhập thời lượng!"

        if not duration.isdigit() or int(duration) <= 0:
            return False, "Thời lượng phải là số nguyên dương!"

        # 2. XỬ LÝ LOGIC (Gọi DAO)
        if mode == "add":
            success = self.movie_dao.add_movie(name, duration, country, genre, actors, lang, age, desc, poster)
            action = "Thêm mới"
        else:
            success = self.movie_dao.update_movie(movie_id, name, duration, country, genre, actors, lang, age, desc,
                                                  poster)
            action = "Cập nhật"

        # 3. TRẢ KẾT QUẢ
        if success:
            return True, f"{action} phim thành công!"
        else:
            return False, f"Lỗi hệ thống: {action} thất bại."