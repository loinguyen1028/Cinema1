from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import joinedload
from db import db
from models import User, Role


class StaffDAO:
    def get_all_staff(self):
        session = db.get_session()
        try:
            return session.query(User).options(joinedload(User.role)) \
                .filter(User.is_active == True) \
                .order_by(User.user_id.desc()).all()
        except Exception:
            return []
        finally:
            session.close()

    def search_staff(self, keyword):
        session = db.get_session()
        try:
            all_staff = session.query(User).options(joinedload(User.role)) \
                .filter(User.is_active == True) \
                .order_by(User.user_id.desc()).all()

            if not keyword:
                return all_staff

            keyword = keyword.lower().strip()
            result = []

            for staff in all_staff:
                username = staff.username.lower() if staff.username else ""

                extra = staff.extra_info if staff.extra_info else {}
                name = extra.get('name', '').lower()
                phone = extra.get('phone', '').lower()
                email = extra.get('email', '').lower()

                if (
                    keyword in username or
                    keyword in name or
                    keyword in phone or
                    keyword in email
                ):
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

            input_phone = phone.strip()
            input_email = email.strip().lower() if email else ""

            existing_users = session.query(User).filter(User.is_active == True).all()

            for u in existing_users:
                extra = u.extra_info if u.extra_info else {}

                u_phone = str(extra.get('phone', '')).strip()
                u_email = str(extra.get('email', '')).strip().lower()

                if u_phone == input_phone:
                    return False, f"Số điện thoại {phone} đã được sử dụng bởi: {u.full_name}"

                if input_email and u_email == input_email:
                    return False, f"Email {email} đã được sử dụng bởi: {u.full_name}"

            extra = {
                "name": name,
                "gender": gender,
                "dob": dob,
                "phone": phone,
                "email": email,
                "start_date": start_date
            }

            new_staff = User(
                username=username,
                password="123456",
                full_name=name,
                role_id=role_id,
                extra_info=extra
            )

            session.add(new_staff)
            session.commit()
            return True, "Thêm nhân viên thành công (Mật khẩu: 123456)"

        except IntegrityError:
            session.rollback()
            return False, "Dữ liệu bị trùng lặp hệ thống!"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            session.close()

    def update_staff(self, staff_id, name, gender, dob, phone, email, start_date, role_id):
        session = db.get_session()
        try:
            user = session.query(User).get(staff_id)
            if not user:
                return False, "Không tìm thấy nhân viên"

            input_phone = phone.strip()
            input_email = email.strip().lower() if email else ""

            others = session.query(User).filter(
                User.is_active == True,
                User.user_id != staff_id
            ).all()

            for u in others:
                extra = u.extra_info if u.extra_info else {}

                u_phone = str(extra.get('phone', '')).strip()
                u_email = str(extra.get('email', '')).strip().lower()

                if u_phone == input_phone:
                    return False, f"Số điện thoại {phone} đang thuộc về: {u.full_name}"

                if input_email and u_email == input_email:
                    return False, f"Email {email} đang thuộc về: {u.full_name}"

            user.role_id = role_id
            user.full_name = name

            extra = dict(user.extra_info) if user.extra_info else {}
            extra.update({
                "name": name,
                "gender": gender,
                "dob": dob,
                "phone": phone,
                "email": email,
                "start_date": start_date
            })
            user.extra_info = extra

            session.commit()
            return True, "Cập nhật thành công!"

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

    def get_by_id(self, staff_id):
        session = db.get_session()
        try:
            return session.query(User).options(joinedload(User.role)).get(staff_id)
        except Exception as e:
            print(f"Lỗi lấy thông tin nhân viên: {e}")
            return None
        finally:
            session.close()
