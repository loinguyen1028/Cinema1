from dao.auth_dao import AuthDAO


class AuthService:
    def __init__(self):
        self.dao = AuthDAO()

    def login(self, username, password):
        # 1. Gọi DAO để lấy user theo username
        user = self.dao.login(username, password)

        if user:
            # 2. KIỂM TRA TRẠNG THÁI (Logic chặn đăng nhập ở đây)
            if user.is_active is False:  # Nếu tài khoản bị khóa
                return None, "Tài khoản đã bị khóa! Vui lòng liên hệ Admin."

            return user, "Đăng nhập thành công"

        return None, "Sai tên đăng nhập hoặc mật khẩu"

    def change_password(self, user_id, old_pass, new_pass, confirm_pass):
        # 1. Validate input
        if not new_pass:
            return False, "Mật khẩu mới không được để trống!"
        if len(new_pass) < 6:
            return False, "Mật khẩu mới phải có ít nhất 6 ký tự!"
        if new_pass != confirm_pass:
            return False, "Mật khẩu xác nhận không khớp!"
        if new_pass == old_pass:
            return False, "Mật khẩu mới không được trùng mật khẩu cũ!"

        # 2. Check DB
        user = self.dao.get_user_by_id(user_id)
        if not user:
            return False, "Không tìm thấy tài khoản!"

        if user.password != old_pass:
            return False, "Mật khẩu cũ không chính xác!"

        # 3. Update
        if self.dao.change_password(user_id, new_pass):
            return True, "Đổi mật khẩu thành công!"
        return False, "Lỗi hệ thống!"