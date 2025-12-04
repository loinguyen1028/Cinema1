from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import Movie

class MovieDAO:
    def get_all_movies(self):
        session = db.get_session()
        try:
            movies = session.query(Movie).order_by(Movie.movie_id.desc()).all()
            return movies
        except SQLAlchemyError:
            return []
        finally:
            session.close()

    def search_movies(self, keyword):
        session = db.get_session()
        try:
            movies = session.query(Movie).filter(Movie.title.ilike(f"%{keyword}%")).order_by(Movie.movie_id.desc()).all()
            return movies
        except SQLAlchemyError:
            return []
        finally:
            session.close()

    # --- CẬP NHẬT HÀM THÊM: Nhận poster_path ---
    def add_movie(self, title, duration, country, genre, actors, language, age_limit, description="", poster_path=""):
        session = db.get_session()
        try:
            info_json = {
                "genre": genre,
                "country": country,
                "actors": actors,       
                "language": language,   
                "age_limit": age_limit  
            }

            new_movie = Movie(
                title=title,
                duration_min=int(duration),
                description=description,
                poster_path=poster_path, # <--- Lưu đường dẫn ảnh vào cột này
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

    # --- CẬP NHẬT HÀM SỬA: Nhận poster_path ---
    def update_movie(self, movie_id, title, duration, country, genre, actors, language, age_limit, description="", poster_path=""):
        session = db.get_session()
        try:
            movie = session.query(Movie).get(movie_id)
            if movie:
                movie.title = title
                movie.duration_min = int(duration)
                movie.description = description
                
                # Chỉ cập nhật poster_path nếu có đường dẫn mới được chọn
                # (Nếu người dùng không chọn ảnh mới, giữ nguyên ảnh cũ)
                if poster_path:
                    movie.poster_path = poster_path

                current_info = dict(movie.extra_info) if movie.extra_info else {}
                
                current_info["genre"] = genre
                current_info["country"] = country
                current_info["actors"] = actors       
                current_info["language"] = language   
                current_info["age_limit"] = age_limit 
                
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
        session = db.get_session()
        try:
            movie = session.query(Movie).get(movie_id)
            if movie:
                session.delete(movie)
                session.commit()
                return True
            return False
        except SQLAlchemyError:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_movie_by_id(self, movie_id):
        """Lấy thông tin chi tiết 1 phim theo ID"""
        session = db.get_session()
        try:
            movie = session.query(Movie).get(movie_id)
            # Truy cập các thuộc tính để nạp dữ liệu trước khi đóng session
            if movie:
                _ = movie.title 
                _ = movie.extra_info
            return movie
        except SQLAlchemyError as e:
            print(f"Lỗi lấy phim: {e}")
            return None
        finally:
            session.close()