from dao.room_dao import RoomDAO


class RoomService:
    def __init__(self):
        self.dao = RoomDAO()

    def get_all(self):
        return self.dao.get_all_rooms()

    def get_by_id(self, room_id):
        return self.dao.get_room_by_id(room_id)

    def save_room(self, mode, room_id, name, total_seats):
        # Validate logic
        if not name:
            return False, "Tên phòng không được để trống"

        try:
            seats_val = int(total_seats)
            if seats_val <= 0:
                return False, "Số lượng ghế phải lớn hơn 0"
        except ValueError:
            return False, "Số lượng ghế phải là số nguyên (không chứa chữ)"

        if mode == "add":
            return self.dao.add_room(name, int(total_seats))
        else:
            return self.dao.update_room(room_id, name, int(total_seats))

    def delete_room(self, room_id):
        # Có thể thêm logic kiểm tra: Phòng đang có suất chiếu chưa chiếu thì không cho xóa
        return self.dao.delete_room(room_id)