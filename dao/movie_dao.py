from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import Movie

class MovieDAO:
    def get_all_movies(self):
        """Lấy danh sách tất cả phim"""
        session = db.get_session()
        try:
            # Sắp xếp theo ID giảm dần để phim mới nhất lên đầu
            movies = session.query(Movie).order_by(Movie.movie_id.desc()).all()
            return movies
        except SQLAlchemyError as e:
            print(f"Lỗi lấy danh sách phim: {e}")
            return []
        finally:
            session.close()

    def add_movie(self, title, duration, country, genre, actors, language, age_limit, description="", poster_path=""):
        session = db.get_session()
        try:
            # Lưu tất cả thông tin phụ vào JSON
            info_json = {
                "genre": genre,
                "country": country,
                "actors": actors,       # Mới
                "language": language,   # Mới (Vietsub/Lồng tiếng)
                "age_limit": age_limit  # Mới (C13, C16...)
            }

            new_movie = Movie(
                title=title,
                duration_min=int(duration),
                description=description,
                poster_path=poster_path,
                extra_info=info_json
            )
            session.add(new_movie)
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Lỗi thêm: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_movie(self, movie_id, title, duration, country, genre, actors, language, age_limit, description=""):
        session = db.get_session()
        try:
            movie = session.query(Movie).get(movie_id)
            if movie:
                movie.title = title
                movie.duration_min = int(duration)
                movie.description = description
                
                # Update JSON an toàn
                current_info = dict(movie.extra_info) if movie.extra_info else {}
                
                current_info["genre"] = genre
                current_info["country"] = country
                current_info["actors"] = actors       # Mới
                current_info["language"] = language   # Mới
                current_info["age_limit"] = age_limit # Mới
                
                movie.extra_info = current_info
                
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Lỗi sửa: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def delete_movie(self, movie_id):
        """Xóa phim theo ID"""
        session = db.get_session()
        try:
            movie = session.query(Movie).get(movie_id)
            if movie:
                session.delete(movie)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Lỗi xóa phim: {e}")
            session.rollback() # Hoàn tác nếu lỗi (vd: phim đang có suất chiếu)
            return False
        finally:
            session.close()

    def search_movies(self, keyword):
        """Tìm kiếm phim theo tên (không phân biệt hoa thường)"""
        session = db.get_session()
        try:
            # ilike tương đương với LIKE '%keyword%' nhưng không phân biệt hoa thường
            movies = session.query(Movie).filter(Movie.title.ilike(f"%{keyword}%")).order_by(Movie.movie_id.desc()).all()
            return movies
        except SQLAlchemyError as e:
            print(f"Lỗi tìm kiếm phim: {e}")
            return []
        finally:
            session.close()