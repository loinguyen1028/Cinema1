from dao.staff_dao import StaffDAO


class StaffService:
    def __init__(self):
        self.dao = StaffDAO()

    def get_all(self):
        return self.dao.get_all_staff()

    def search(self, keyword):
        return self.dao.search_staff(keyword)

    def get_roles(self):
        return self.dao.get_all_roles()

    def save_staff(self, mode, staff_id, data):
        # Validate
        if not data['name']: return False, "Họ tên không được để trống"
        if not data['phone']: return False, "SĐT không được để trống"

        if mode == "add":
            if not data['username']: return False, "Tài khoản không được để trống"
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

    def delete_staff(self, staff_id):
        return self.dao.delete_staff(staff_id)

    def reset_password(self, staff_id, new_pass, confirm_pass):
        if not new_pass or len(new_pass) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự"
        if new_pass != confirm_pass:
            return False, "Mật khẩu nhập lại không khớp"

        if self.dao.update_password(staff_id, new_pass):
            return True, "Đổi mật khẩu thành công"
        return False, "Lỗi Database"