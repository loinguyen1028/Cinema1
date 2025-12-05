from dao.auth_dao import AuthDAO

class AuthController:
    def __init__(self):
        self.dao = AuthDAO()

    def change_password(self, user_id, old_pass, new_pass, confirm_pass):
        # 1. Lấy thông tin user hiện tại để check pass cũ
        user = self.dao.get_user_by_id(user_id)
        if not user:
            return False, "Không tìm thấy tài khoản!"

        # 2. Kiểm tra mật khẩu cũ
        if user.password != old_pass:
            return False, "Mật khẩu cũ không chính xác!"

        # 3. Validate mật khẩu mới
        if not new_pass:
            return False, "Mật khẩu mới không được để trống!"
        if len(new_pass) < 6:
            return False, "Mật khẩu mới phải có ít nhất 6 ký tự!"
        if new_pass != confirm_pass:
            return False, "Mật khẩu xác nhận không khớp!"
        if new_pass == old_pass:
            return False, "Mật khẩu mới không được trùng mật khẩu cũ!"

        # 4. Cập nhật
        if self.dao.change_password(user_id, new_pass):
            return True, "Đổi mật khẩu thành công!"
        else:
            return False, "Lỗi hệ thống khi cập nhật!"