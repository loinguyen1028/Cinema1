from services.room_service import RoomService

class RoomController:
    def __init__(self):
        self.service = RoomService()

    def get_all_rooms(self):
        return self.service.get_all()

    def get_room_by_id(self, room_id):
        return self.service.get_by_id(room_id)

    def save_room(self, mode, room_id, room_name, rows, seats_per_row):
        return self.service.save_room(
            mode, room_id, room_name, rows, seats_per_row
        )

    def delete_room(self, room_id):
        return self.service.delete_room(room_id)
