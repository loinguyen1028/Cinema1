from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import Movie


class MovieDAO:
    def get_all_movies(self):
        session = db.get_session()
        try:
            return session.query(Movie).filter_by(is_active=True).order_by(Movie.movie_id.desc()).all()
        finally:
            session.close()

    def get_movie_by_id(self, movie_id):
        session = db.get_session()
        try:
            return session.query(Movie).get(movie_id)
        finally:
            session.close()

    def add_movie(self, title, duration, country, genre, actors, language, age_limit, description, poster_path):
        session = db.get_session()
        try:
            extra = {
                "country": country, "genre": genre, "actors": actors,
                "language": language, "age_limit": age_limit
            }
            new_movie = Movie(
                title=title, duration_min=int(duration),
                description=description, poster_path=poster_path,
                extra_info=extra
            )
            session.add(new_movie)
            session.commit()
            return True, "Thêm phim thành công"
        except IntegrityError:
            session.rollback()
            return False, "Phim này đã tồn tại!"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def update_movie(self, movie_id, title, duration, country, genre, actors, language, age_limit, description,
                     poster_path):
        session = db.get_session()
        try:
            m = session.query(Movie).get(movie_id)
            if m:
                m.title = title
                m.duration_min = int(duration)
                m.description = description
                if poster_path: m.poster_path = poster_path

                extra = dict(m.extra_info) if m.extra_info else {}
                extra.update({
                    "country": country, "genre": genre, "actors": actors,
                    "language": language, "age_limit": age_limit
                })
                m.extra_info = extra

                session.commit()
                return True, "Cập nhật thành công"
            return False, "Không tìm thấy phim"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def delete_movie(self, movie_id):
        session = db.get_session()
        try:
            m = session.query(Movie).get(movie_id)
            if m:
                m.is_active = False  # Xóa mềm
                session.commit()
                return True, "Đã xóa phim"
            return False, "Không tìm thấy phim"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def search_movies(self, keyword):
        session = db.get_session()
        try:
            return session.query(Movie).filter(Movie.title.ilike(f"%{keyword}%")).filter_by(is_active=True).all()
        finally:
            session.close()