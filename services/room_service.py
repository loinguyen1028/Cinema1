import string
from dao.room_dao import RoomDAO

class RoomService:
    def __init__(self):
        self.dao = RoomDAO()

    def get_all(self):
        return self.dao.get_all_rooms()

    def get_by_id(self, room_id):
        return self.dao.get_room_by_id(room_id)

    def save_room(self, mode, room_id, room_name, rows, seats_per_row):
        if not room_name:
            return False, "Tên phòng không được để trống"

        try:
            rows = int(rows)
            seats_per_row = int(seats_per_row)
        except ValueError:
            return False, "Số hàng và số ghế phải là số"

        if rows <= 0 or seats_per_row <= 0:
            return False, "Số hàng và số ghế phải > 0"

        if rows > 26:
            return False, "Số hàng tối đa là 26 (A-Z)"

        capacity = rows * seats_per_row

        if mode == "add":
            return self.dao.create_room_with_seats(
                room_name=room_name,
                rows=rows,
                seats_per_row=seats_per_row,
                capacity=capacity
            )

        elif mode == "edit":
            return self.dao.update_room_with_seats(
                room_id=room_id,
                room_name=room_name,
                rows=rows,
                seats_per_row=seats_per_row,
                capacity=capacity
            )

        return False, "Mode không hợp lệ"

    def delete_room(self, room_id):
        return self.dao.delete_room(room_id)
