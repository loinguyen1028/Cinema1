from db import db
from models import Room, Seat, Showtime
from sqlalchemy.exc import IntegrityError
import string
from sqlalchemy.orm import joinedload


class RoomDAO:

    def get_all_rooms(self):
        session = db.get_session()
        try:
            return session.query(Room) \
                .filter(Room.is_active == True) \
                .order_by(Room.room_id) \
                .all()
        finally:
            session.close()

    def get_room_by_id(self, room_id):
        session = db.get_session()
        try:
            return session.query(Room) \
                .options(joinedload(Room.seats)) \
                .filter(Room.room_id == room_id) \
                .first()
        finally:
            session.close()

    def create_room_with_seats(self, room_name, rows, seats_per_row, capacity):
        session = db.get_session()
        try:
            room = Room(room_name=room_name, capacity=capacity)
            session.add(room)
            session.flush()

            seat_rows = string.ascii_uppercase[:rows]
            for row in seat_rows:
                for num in range(1, seats_per_row + 1):
                    session.add(Seat(
                        room_id=room.room_id,
                        seat_row=row,
                        seat_number=num
                    ))

            session.commit()
            return True, "Thêm phòng & ghế thành công"

        except IntegrityError:
            session.rollback()
            return False, "Tên phòng đã tồn tại"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def update_room_with_seats(self, room_id, room_name, rows, seats_per_row, capacity):
        session = db.get_session()
        try:
            room = session.get(Room, room_id)
            if not room:
                return False, "Không tìm thấy phòng"

            has_showtime = session.query(Showtime) \
                .filter(Showtime.room_id == room_id) \
                .first()
            if has_showtime:
                return False, "Không thể sửa cấu trúc phòng đã có suất chiếu"

            room.room_name = room_name
            room.capacity = capacity

            session.query(Seat) \
                .filter(Seat.room_id == room_id) \
                .delete()

            seat_rows = string.ascii_uppercase[:rows]
            for row in seat_rows:
                for num in range(1, seats_per_row + 1):
                    session.add(Seat(
                        room_id=room_id,
                        seat_row=row,
                        seat_number=num
                    ))

            session.commit()
            return True, "Cập nhật phòng & ghế thành công"

        except IntegrityError:
            session.rollback()
            return False, "Tên phòng đã tồn tại"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def update_room_name(self, room_id, room_name):
        session = db.get_session()
        try:
            room = session.get(Room, room_id)
            if not room:
                return False, "Không tìm thấy phòng"

            has_showtime = session.query(Showtime) \
                .filter(Showtime.room_id == room_id) \
                .first()
            if has_showtime:
                return False, "Không thể sửa phòng đã có suất chiếu"

            room.room_name = room_name
            session.commit()
            return True, "Cập nhật phòng thành công"

        except IntegrityError:
            session.rollback()
            return False, "Tên phòng đã tồn tại"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def delete_room(self, room_id):
        session = db.get_session()
        try:
            room = session.get(Room, room_id)
            if not room:
                return False, "Không tìm thấy phòng"

            room.is_active = False
            session.commit()
            return True, "Đã xóa phòng"

        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
