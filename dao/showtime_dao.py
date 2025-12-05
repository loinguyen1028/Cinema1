from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from sqlalchemy.orm import joinedload  # <--- QUAN TRỌNG: Import cái này
from db import db
from models import Showtime, Movie, Room
from datetime import datetime


class ShowtimeDAO:
    def get_all_showtimes(self):
        """Lấy tất cả suất chiếu, nạp luôn Movie và Room"""
        session = db.get_session()
        try:
            # Dùng joinedload để nạp trước dữ liệu quan hệ
            return session.query(Showtime).options(
                joinedload(Showtime.movie),
                joinedload(Showtime.room)
            ).order_by(Showtime.start_time.desc()).all()
        finally:
            session.close()

    def filter_showtimes(self, date_str=None, room_name=None):
        """Lọc suất chiếu, nạp luôn Movie và Room"""
        session = db.get_session()
        try:
            # Thêm options(joinedload(...)) vào câu query
            query = session.query(Showtime).options(
                joinedload(Showtime.movie),
                joinedload(Showtime.room)
            ).join(Room)

            if date_str:
                search_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                query = query.filter(func.date(Showtime.start_time) == search_date)

            if room_name and room_name != "Toàn bộ":
                query = query.filter(Room.room_name == room_name)

            return query.order_by(Showtime.start_time).all()
        except Exception as e:
            print(f"Lỗi filter: {e}")
            return []
        finally:
            session.close()

    # ... (Các hàm add, update, delete giữ nguyên như cũ) ...
    def add_showtime(self, movie_id, room_id, start_datetime, price):
        session = db.get_session()
        try:
            new_st = Showtime(
                movie_id=movie_id, room_id=room_id,
                start_time=start_datetime, ticket_price=price
            )
            session.add(new_st)
            session.commit()
            return True
        except Exception as e:
            print(f"Lỗi thêm: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update_showtime(self, st_id, movie_id, room_id, start_datetime, price):
        session = db.get_session()
        try:
            st = session.query(Showtime).get(st_id)
            if st:
                st.movie_id = movie_id
                st.room_id = room_id
                st.start_time = start_datetime
                st.ticket_price = price
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"Lỗi sửa: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def delete_showtime(self, st_id):
        session = db.get_session()
        try:
            st = session.query(Showtime).get(st_id)
            if st:
                session.delete(st)
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    # ... (Các hàm helper giữ nguyên, nhưng hàm get_showtime_by_id cần sửa) ...
    def get_movies_list(self):
        session = db.get_session()
        try:
            return session.query(Movie).all()
        finally:
            session.close()

    def get_rooms_list(self):
        session = db.get_session()
        try:
            return session.query(Room).all()
        finally:
            session.close()

    def get_showtime_by_id(self, st_id):
        """Lấy chi tiết 1 suất chiếu, nạp luôn Movie và Room"""
        session = db.get_session()
        try:
            # Thêm joinedload ở đây nữa để dùng cho chức năng Xem/Sửa
            return session.query(Showtime).options(
                joinedload(Showtime.movie),
                joinedload(Showtime.room)
            ).get(st_id)
        finally:
            session.close()