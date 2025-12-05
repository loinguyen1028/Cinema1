from dao.customer_dao import CustomerDAO


class CustomerController:
    def __init__(self):
        self.dao = CustomerDAO()

    def get_all(self):
        return self.dao.get_all()

    def search(self, keyword):
        return self.dao.search(keyword)

    def get_detail(self, customer_id):
        return self.dao.get_by_id(customer_id)

    def delete(self, customer_id):
        if self.dao.delete(customer_id):
            return True, "Xóa thành công!"
        return False, "Không thể xóa (có thể khách hàng này đã có vé đặt)."

    def save(self, mode, customer_id, name, phone, email, dob, points, level):
        # Validate
        if not name:
            return False, "Tên khách hàng không được để trống!"
        if not phone:
            return False, "Số điện thoại không được để trống!"

        # Gọi DAO
        if mode == "add":
            success = self.dao.add(name, phone, email, dob, points, level)
            action = "Thêm mới"
        else:
            success = self.dao.update(customer_id, name, phone, email, dob, points, level)
            action = "Cập nhật"

        if success:
            return True, f"{action} thành công!"
        else:
            return False, f"{action} thất bại (Có thể SĐT đã tồn tại)."