from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from db import db
from models import User, Role


class StaffDAO:
    def get_all_staff(self):
        session = db.get_session()
        try:
            return session.query(User).options(joinedload(User.role)).order_by(User.user_id.desc()).all()
        finally:
            session.close()

    def search_staff(self, keyword):
        session = db.get_session()
        try:
            return session.query(User).options(joinedload(User.role)).filter(
                (User.full_name.ilike(f"%{keyword}%")) |
                (User.username.ilike(f"%{keyword}%"))
            ).all()
        finally:
            session.close()

    def get_by_id(self, staff_id):
        session = db.get_session()
        try:
            return session.query(User).options(joinedload(User.role)).get(staff_id)
        finally:
            session.close()

    # --- HÀM MỚI: LẤY DANH SÁCH ROLE TỪ DB ---
    def get_all_roles(self):
        session = db.get_session()
        try:
            return session.query(Role).all()
        finally:
            session.close()

    # --- CẬP NHẬT: Nhận role_id trực tiếp ---
    def add_staff(self, name, gender, dob, phone, email, start_date, username, role_id):
        session = db.get_session()
        try:
            # Gom thông tin phụ vào JSON (Bỏ ui_role)
            info = {
                "gender": gender,
                "dob": dob,
                "phone": phone,
                "email": email,
                "start_date": start_date
            }

            new_user = User(
                username=username,
                password="123456",  # Mặc định
                full_name=name,
                role_id=role_id,  # <--- Gán Role ID từ giao diện
                extra_info=info
            )
            session.add(new_user)
            session.commit()
            return True, "Thêm thành công"
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()

    def update_staff(self, staff_id, name, gender, dob, phone, email, start_date, role_id):
        session = db.get_session()
        try:
            user = session.query(User).get(staff_id)
            if user:
                user.full_name = name
                user.role_id = role_id  # <--- Cập nhật Role ID

                current_info = dict(user.extra_info) if user.extra_info else {}
                current_info.update({
                    "gender": gender,
                    "dob": dob,
                    "phone": phone,
                    "email": email,
                    "start_date": start_date
                })
                user.extra_info = current_info

                session.commit()
                return True, "Cập nhật thành công"
            return False, "Không tìm thấy nhân viên"
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()

    def delete_staff(self, staff_id):
        # (Giữ nguyên như cũ)
        session = db.get_session()
        try:
            user = session.query(User).get(staff_id)
            if user:
                session.delete(user)
                session.commit()
                return True, "Đã xóa nhân viên"
            return False, "Không tìm thấy nhân viên"
        except SQLAlchemyError:
            session.rollback()
            return False, "Lỗi: Không thể xóa (có thể do ràng buộc dữ liệu)"
        finally:
            session.close()
