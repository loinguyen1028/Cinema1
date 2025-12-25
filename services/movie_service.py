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
        if self.movie_dao.delete_movie(movie_id):
            return True, "Xóa phim thành công!"
        return False, "Lỗi: Không thể xóa phim này (có thể do ràng buộc dữ liệu)."

    def save_movie(self, mode, movie_id, name, duration, country, genre, actors, lang, age, desc, poster):
        """
        Hàm xử lý chung cho cả Thêm và Sửa
        """
        name = name.strip()
        duration = str(duration).strip()

        if not name:
            return False, "Vui lòng nhập tên phim!"

        if not duration:
            return False, "Vui lòng nhập thời lượng!"

        try:
            dur_val = int(duration)
            if dur_val <= 0:
                return False, "Thời lượng phải lớn hơn 0 phút!"
        except ValueError:
            return False, "Thời lượng phải là số nguyên (không chứa chữ)!"

        if mode == "add":
            success, db_msg = self.movie_dao.add_movie(
                name, dur_val,
                country.strip(), genre, actors.strip(), lang.strip(),
                age, desc, poster
            )
        else:
            success, db_msg = self.movie_dao.update_movie(
                movie_id, name, dur_val,
                country.strip(), genre, actors.strip(), lang.strip(),
                age, desc, poster
            )


        return success, db_msg