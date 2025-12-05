from db import db
from models import Room

class RoomDAO:
    def get_all_rooms(self):
        session = db.get_session()
        try:
            return session.query(Room).all()
        finally:
            session.close()

    def add_room(self, room_name, capacity):
        session = db.get_session()
        try:
            new_room = Room(room_name=room_name, capacity=capacity)
            session.add(new_room)
            session.commit()
            return True, "Thêm phòng thành công"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi thêm phòng: {e}"
        finally:
            session.close()

    def update_room(self, room_id, room_name, capacity):
        session = db.get_session()
        try:
            room = session.query(Room).get(room_id)
            if room:
                room.room_name = room_name
                room.capacity = capacity
                session.commit()
                return True, "Cập nhật phòng thành công"
            return False, "Phòng không tồn tại"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi cập nhật phòng: {e}"
        finally:
            session.close()

    def delete_room(self, room_id):
        session = db.get_session()
        try:
            room = session.query(Room).get(room_id)
            if room:
                session.delete(room)
                session.commit()
                return True, "Xóa phòng thành công"
            return False, "Phòng không tồn tại"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi xóa phòng: {e}"
        finally:
            session.close()
