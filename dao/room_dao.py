from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import Room

class RoomDAO:
    def get_all_rooms(self):
        session = db.get_session()
        try:
            return session.query(Room).filter_by(is_active=True).order_by(Room.room_id).all()
        finally:
            session.close()

    def get_room_by_id(self, room_id):
        session = db.get_session()
        try:
            return session.query(Room).get(room_id)
        finally:
            session.close()

    def add_room(self, name, capacity):
        session = db.get_session()
        try:
            new_room = Room(room_name=name, capacity=capacity)
            session.add(new_room)
            session.commit()
            return True, "Thêm phòng thành công"
        except IntegrityError:
            session.rollback()
            return False, "Tên phòng có thể đã tồn tại"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def update_room(self, room_id, name, capacity):
        session = db.get_session()
        try:
            room = session.query(Room).get(room_id)
            if room:
                room.room_name = name
                room.capacity = capacity
                session.commit()
                return True, "Cập nhật thành công"
            return False, "Không tìm thấy phòng"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def delete_room(self, room_id):
        session = db.get_session()
        try:
            room = session.query(Room).get(room_id)
            if room:
                room.is_active = False # Xóa mềm
                session.commit()
                return True, "Đã xóa phòng"
            return False, "Không tìm thấy phòng"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()