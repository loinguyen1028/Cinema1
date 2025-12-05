from dao.RoomDAO import RoomDAO  # DAO xử lý trực tiếp với CSDL

class RoomController:
    def __init__(self):
        self.room_dao = RoomDAO()

    def get_all_rooms(self):
        return self.room_dao.get_all_rooms()

    def add_room(self, room_name, capacity):
        return self.room_dao.add_room(room_name, capacity)

    def update_room(self, room_id, room_name, capacity):
        return self.room_dao.update_room(room_id, room_name, capacity)

    def delete_room(self, room_id):
        return self.room_dao.delete_room(room_id)
