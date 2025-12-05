from dao.staff_dao import StaffDAO

class StaffController:
    def __init__(self):
        self.dao = StaffDAO()

    def get_all(self):
        return self.dao.get_all_staff()

    def search(self, keyword):
        return self.dao.search_staff(keyword)

    def get_detail(self, staff_id):
        return self.dao.get_by_id(staff_id)

    def delete(self, staff_id):
        return self.dao.delete_staff(staff_id)

    # --- MỚI ---
    def get_roles(self):
        return self.dao.get_all_roles()

    def save(self, mode, staff_id, data):
        # Validate
        if not data['name']: return False, "Họ tên không được để trống"
        if not data['username'] and mode == "add": return False, "Tài khoản không được để trống"
        if not data['role_id']: return False, "Vui lòng chọn Quyền hạn"

        if mode == "add":
            return self.dao.add_staff(
                data['name'], data['gender'], data['dob'],
                data['phone'], data['email'],
                data['start_date'], data['username'], data['role_id']
            )
        else:
            return self.dao.update_staff(
                staff_id,
                data['name'], data['gender'], data['dob'],
                data['phone'], data['email'],
                data['start_date'], data['role_id']
            )

    def reset_password(self, staff_id, new_pass, confirm_pass):
        # 1. Validate
        if not new_pass:
            return False, "Mật khẩu không được để trống"

        if len(new_pass) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự"

        if new_pass != confirm_pass:
            return False, "Mật khẩu nhập lại không khớp"

        # 2. Gọi DAO
        if self.dao.update_password(staff_id, new_pass):
            return True, "Đổi mật khẩu thành công"
        else:
            return False, "Lỗi cập nhật Database"