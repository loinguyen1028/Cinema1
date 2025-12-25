from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy import cast, Date
from db import db
from models import Showtime, Movie, Room
from datetime import datetime


class ShowtimeDAO:
    def filter_showtimes(self, date_str=None, room_filter=None):
        session = db.get_session()
        try:
            query = session.query(Showtime).options(
                joinedload(Showtime.movie),
                joinedload(Showtime.room)
            ).filter(Showtime.is_active == True)

            if date_str:
                try:
                    search_date = datetime.strptime(date_str, "%d/%m/%Y").date()
                    query = query.filter(cast(Showtime.start_time, Date) == search_date)
                except ValueError:
                    pass

            if room_filter and room_filter not in ["Toàn bộ", "Tất cả"]:
                query = query.join(Room).filter(Room.room_name == room_filter)

            return query.order_by(Showtime.start_time).all()
        finally:
            session.close()

    def get_showtime_by_id(self, st_id):
        session = db.get_session()
        try:
            return session.query(Showtime).options(
                joinedload(Showtime.movie),
                joinedload(Showtime.room)
            ).get(st_id)
        finally:
            session.close()

    def add_showtime(self, movie_id, room_id, start_time, price):
        session = db.get_session()
        try:
            st = Showtime(
                movie_id=movie_id,
                room_id=room_id,
                start_time=start_time,
                ticket_price=price
            )
            session.add(st)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def update_showtime(self, st_id, movie_id, room_id, start_time, price):
        session = db.get_session()
        try:
            st = session.query(Showtime).get(st_id)
            if st:
                st.movie_id = movie_id
                st.room_id = room_id
                st.start_time = start_time
                st.ticket_price = price
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def delete_showtime(self, st_id):
        session = db.get_session()
        try:
            st = session.query(Showtime).get(st_id)
            if st:
                st.is_active = False
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def get_showtimes_by_room_date(self, room_id, check_date):
        session = db.get_session()
        try:
            return session.query(Showtime).options(
                joinedload(Showtime.movie)
            ).filter(
                Showtime.room_id == room_id,
                Showtime.is_active == True,
                cast(Showtime.start_time, Date) == check_date
            ).all()
        finally:
            session.close()
