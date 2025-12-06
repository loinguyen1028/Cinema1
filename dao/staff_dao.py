from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload
from db import db
from models import User, Role


class StaffDAO:
    def get_all_staff(self):
        session = db.get_session()
        try:
            # Lấy tất cả user trừ Admin (role_id=1 thường là admin)
            # Và phải là is_active=True
            return session.query(User).options(joinedload(User.role)) \
                .filter(User.is_active == True) \
                .order_by(User.user_id.desc()).all()
        except Exception:
            return []
        finally:
            session.close()

    # --- HÀM MỚI BỔ SUNG: TÌM KIẾM NHÂN VIÊN ---
    def search_staff(self, keyword):
        """
        Tìm kiếm nhân viên theo Username, Tên, SĐT hoặc Email.
        (Xử lý lọc bằng Python vì dữ liệu nằm trong JSON)
        """
        session = db.get_session()
        try:
            # Lấy toàn bộ nhân viên đang hoạt động
            all_staff = session.query(User).options(joinedload(User.role)) \
                .filter(User.is_active == True) \
                .order_by(User.user_id.desc()).all()

            if not keyword:
                return all_staff

            keyword = keyword.lower().strip()
            result = []

            for staff in all_staff:
                # 1. Kiểm tra Username
                username = staff.username.lower() if staff.username else ""

                # 2. Kiểm tra thông tin trong JSON extra_info
                extra = staff.extra_info if staff.extra_info else {}
                name = extra.get('name', '').lower()
                phone = extra.get('phone', '').lower()
                email = extra.get('email', '').lower()

                # 3. So sánh: Nếu từ khóa nằm trong bất kỳ trường nào -> Chọn
                if (keyword in username) or (keyword in name) or (keyword in phone) or (keyword in email):
                    result.append(staff)

            return result
        except Exception as e:
            print(f"Lỗi tìm kiếm nhân viên: {e}")
            return []
        finally:
            session.close()

    def get_all_roles(self):
        session = db.get_session()
        try:
            return session.query(Role).all()
        finally:
            session.close()

    def add_staff(self, name, gender, dob, phone, email, start_date, username, role_id):
        session = db.get_session()
        try:
            if session.query(User).filter_by(username=username).first():
                return False, f"Tài khoản '{username}' đã tồn tại!"

            extra = {
                "name": name, "gender": gender, "dob": dob,
                "phone": phone, "email": email, "start_date": start_date
            }

            # Mật khẩu mặc định là 123456
            new_staff = User(username=username, password="123456", role_id=role_id, extra_info=extra)
            session.add(new_staff)
            session.commit()
            return True, "Thêm nhân viên thành công (Mật khẩu: 123456)"

        except IntegrityError:
            session.rollback()
            return False, "Tài khoản hoặc dữ liệu bị trùng lặp!"
        except SQLAlchemyError as e:
            session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            session.close()

    def update_staff(self, staff_id, name, gender, dob, phone, email, start_date, role_id):
        session = db.get_session()
        try:
            user = session.query(User).get(staff_id)
            if user:
                user.role_id = role_id

                extra = dict(user.extra_info) if user.extra_info else {}
                extra.update({
                    "name": name, "gender": gender, "dob": dob,
                    "phone": phone, "email": email, "start_date": start_date
                })
                user.extra_info = extra

                session.commit()
                return True, "Cập nhật thành công!"
            return False, "Không tìm thấy nhân viên"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()

    def delete_staff(self, staff_id):
        session = db.get_session()
        try:
            user = session.query(User).get(staff_id)
            if user:
                user.is_active = False
                session.commit()
                return True, "Đã xóa nhân viên"
            return False, "Không tìm thấy nhân viên"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()

    def update_password(self, staff_id, new_pass):
        session = db.get_session()
        try:
            user = session.query(User).get(staff_id)
            if user:
                user.password = new_pass
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()