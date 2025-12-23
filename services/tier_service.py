from dao.tier_dao import TierDAO


class TierService:
    def __init__(self):
        self.dao = TierDAO()

    def get_all(self):
        return self.dao.get_all()

    def get_detail(self, tier_id):
        return self.dao.get_by_id(tier_id)

    def save_tier(self, mode, tier_id, name, min_point, discount):
        # --- 1. VALIDATION LOGIC (Kiểm tra dữ liệu) ---
        if not name or not name.strip():
            return False, "Tên hạng không được để trống"

        try:
            point_val = int(min_point)
            if point_val < 0:
                return False, "Điểm tối thiểu không được âm"
        except ValueError:
            return False, "Điểm phải là số nguyên"

        try:
            discount_val = float(discount)
            if discount_val < 0 or discount_val > 100:
                return False, "Giảm giá phải từ 0% đến 100%"
        except ValueError:
            return False, "Giảm giá phải là số thực"

        # --- 2. GỌI DAO ĐỂ LƯU ---
        if mode == "add":
            return self.dao.add(name.strip(), point_val, discount_val)
        else:
            return self.dao.update(tier_id, name.strip(), point_val, discount_val)

    def delete_tier(self, tier_id):
        # Có thể thêm logic kiểm tra trước khi xóa ở đây nếu cần
        return self.dao.delete(tier_id)