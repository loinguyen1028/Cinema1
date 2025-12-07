import re
from dao.staff_dao import StaffDAO


class StaffService:
    def __init__(self):
        self.dao = StaffDAO()

    def get_all(self):
        return self.dao.get_all_staff()

    def get_by_id(self, staff_id):
        return self.dao.get_by_id(staff_id)

    def search(self, keyword):
        return self.dao.search_staff(keyword)

    def get_roles(self):
        return self.dao.get_all_roles()

    def save_staff(self, mode, staff_id, data):
        name = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        username = data.get('username', '').strip()

        # Kiểm tra rỗng
        if not name: return False, "Họ tên không được để trống"
        if not phone: return False, "SĐT không được để trống"

        # Kiểm tra định dạng Số điện thoại (Phải là số, độ dài 9-11)
        if not phone.isdigit():
            return False, "Số điện thoại chỉ được chứa các chữ số (0-9)!"
        if len(phone) < 9 or len(phone) > 11:
            return False, "Số điện thoại phải từ 9 đến 11 số!"
        if not phone.startswith("0"):
            return False, "Số điện thoại phải bắt đầu bằng số 0!"

        # Kiểm tra định dạng Email (Nếu có nhập)
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "Định dạng Email không hợp lệ (Ví dụ: user@example.com)"

        if mode == "add":
            if not username: return False, "Tài khoản không được để trống"

            # Kiểm tra username không được chứa dấu cách hoặc ký tự đặc biệt
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                return False, "Tài khoản chỉ được chứa chữ, số và dấu gạch dưới!"

            return self.dao.add_staff(
                name, data['gender'], data['dob'],
                phone, email,
                data['start_date'], username, data['role_id']
            )
        else:
            return self.dao.update_staff(
                staff_id,
                name, data['gender'], data['dob'],
                phone, email,
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