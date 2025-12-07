import re
from dao.customer_dao import CustomerDAO

class CustomerService:
    def __init__(self):
        self.dao = CustomerDAO()

    def get_all(self):
        return self.dao.get_all()

    def search(self, keyword):
        return self.dao.search(keyword)

    def get_detail(self, cid):
        return self.dao.get_by_id(cid)

    def save_customer(self, mode, customer_id, name, phone, email, dob, points, level):
        if not name: return False, "Tên không được rỗng"
        if not phone: return False, "SĐT không được rỗng"
        if not phone.isdigit():
            return False, "Số điện thoại chỉ được chứa các chữ số (0-9)!"
        if len(phone) < 9 or len(phone) > 11:
            return False, "Số điện thoại phải từ 9 đến 11 số!"
        if not phone.startswith("0"):
            return False, "Số điện thoại phải bắt đầu bằng số 0!"

        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False, "Định dạng Email không hợp lệ (Ví dụ: user@example.com)"
        try:
            points_val = int(points)
            if points_val < 0:
                return False, "Điểm tích lũy không được âm"
        except ValueError:
            return False, "Điểm tích lũy phải là số nguyên"

        if mode == "add":
            return self.dao.add(name, phone, email, dob, points, level)
        else:
            return self.dao.update(customer_id, name, phone, email, dob, points, level)

    def delete_customer(self, cid):
        if self.dao.delete(cid):
            return True, "Xóa thành công"
        return False, "Lỗi khi xóa (Có thể khách đã có lịch sử giao dịch)"