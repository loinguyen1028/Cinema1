from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError, OperationalError
from db import db
from models import Customer


class CustomerDAO:
    # -----------------------------------------------------
    # CÁC HÀM LẤY DỮ LIỆU (GET)
    # -----------------------------------------------------
    def get_all(self):
        session = db.get_session()
        try:
            return session.query(Customer).filter_by(is_active=True).order_by(Customer.customer_id.desc()).all()
        except Exception:
            return []
        finally:
            session.close()

    def get_by_phone(self, phone):
        session = db.get_session()
        try:
            return session.query(Customer).filter_by(phone=phone).first()
        except Exception:
            return None
        finally:
            session.close()

    def get_by_id(self, customer_id):
        session = db.get_session()
        try:
            return session.query(Customer).get(customer_id)
        except Exception:
            return None
        finally:
            session.close()

    def search(self, keyword):
        session = db.get_session()
        try:
            return session.query(Customer).filter(
                (Customer.name.ilike(f"%{keyword}%")) |
                (Customer.phone.ilike(f"%{keyword}%"))
            ).filter_by(is_active=True).all()
        except Exception:
            return []
        finally:
            session.close()

    # -----------------------------------------------------
    # CÁC HÀM TÁC ĐỘNG DỮ LIỆU (ADD / UPDATE / DELETE)
    # -----------------------------------------------------
    def add(self, name, phone, email, dob, points, level):
        session = db.get_session()
        try:
            # =================================================
            # BƯỚC 1: KIỂM TRA THỦ CÔNG (MANUAL CHECK)
            # =================================================

            # 1. Kiểm tra trùng Số điện thoại
            # (Vì SĐT là bắt buộc và duy nhất)
            if session.query(Customer).filter_by(phone=phone).first():
                return False, f"Số điện thoại {phone} đã tồn tại trong hệ thống!"

            # 2. Kiểm tra trùng Email
            # (Chỉ kiểm tra nếu người dùng CÓ nhập email)
            if email and email.strip():
                # Tìm trong DB xem có ai đang dùng email này không
                exists_email = session.query(Customer).filter(Customer.email == email.strip()).first()
                if exists_email:
                    return False, f"Email '{email}' đã được sử dụng bởi khách hàng khác!"

            extra = {
                "dob": dob,
                "points": int(points) if str(points).isdigit() else 0,
                "level": level
            }

            new_cus = Customer(name=name, phone=phone, email=email, extra_info=extra)
            session.add(new_cus)
            session.commit()

            return True, "Thêm khách hàng thành công!"

        except IntegrityError:
            # Vẫn giữ lại để phòng hờ các lỗi ràng buộc khác
            session.rollback()
            return False, "Lỗi dữ liệu: Thông tin bị trùng lặp!"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            session.close()

    def update(self, customer_id, name, phone, email, dob, points, level):
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if not cus:
                return False, "Không tìm thấy khách hàng cần sửa!"

            # --- 1. KIỂM TRA TRÙNG SĐT (Với người khác) ---
            # Tìm khách hàng có SĐT này NHƯNG có ID khác với khách đang sửa
            exist_phone = session.query(Customer).filter(
                Customer.phone == phone,
                Customer.customer_id != customer_id
            ).first()

            if exist_phone:
                return False, f"Số điện thoại {phone} đang thuộc về khách hàng: {exist_phone.name}"

            # --- 2. KIỂM TRA TRÙNG EMAIL (Với người khác) ---
            if email and email.strip():
                exist_email = session.query(Customer).filter(
                    Customer.email == email.strip(),
                    Customer.customer_id != customer_id
                ).first()

                if exist_email:
                    return False, f"Email '{email}' đang thuộc về khách hàng: {exist_email.name}"

            # --- 3. CẬP NHẬT ---
            cus.name = name
            cus.phone = phone
            cus.email = email

            extra = dict(cus.extra_info) if cus.extra_info else {}
            extra["dob"] = dob
            extra["points"] = int(points) if str(points).isdigit() else 0
            extra["level"] = level
            cus.extra_info = extra

            session.commit()
            return True, "Cập nhật thành công!"

        except Exception as e:
            session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            session.close()

    def delete(self, customer_id):
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if not cus:
                return False, "Không tìm thấy khách hàng!"

            # Xóa mềm (Soft Delete)
            cus.is_active = False
            session.commit()
            return True, "Đã xóa khách hàng thành công!"

        except Exception as e:
            session.rollback()
            return False, f"Lỗi khi xóa: {str(e)}"
        finally:
            session.close()

    # -----------------------------------------------------
    # CÁC HÀM NGHIỆP VỤ KHÁC (TÍCH ĐIỂM)
    # -----------------------------------------------------
    def update_membership(self, customer_id, amount_paid):
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if cus:
                # 10k = 1 điểm
                points_added = int(amount_paid / 10000)

                current_info = dict(cus.extra_info) if cus.extra_info else {}
                current_points = current_info.get("points", 0)

                new_points = current_points + points_added

                # Logic thăng hạng
                new_level = "Thân thiết"
                if new_points >= 2000:
                    new_level = "Kim cương"
                elif new_points >= 1000:
                    new_level = "Vàng"
                elif new_points >= 500:
                    new_level = "Bạc"

                current_info["points"] = new_points
                current_info["level"] = new_level

                cus.extra_info = current_info
                session.commit()
                return True, f"Cộng {points_added} điểm. Hạng: {new_level}"
            return False, "Khách hàng không tồn tại"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def deduct_points(self, customer_id, points_to_use):
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if not cus:
                return False, "Không tìm thấy khách hàng"

            current_info = dict(cus.extra_info) if cus.extra_info else {}
            current_points = current_info.get("points", 0)

            if current_points < points_to_use:
                return False, f"Không đủ điểm (Có: {current_points})"

            new_points = current_points - points_to_use
            current_info["points"] = new_points
            cus.extra_info = current_info

            session.commit()
            return True, f"Đã trừ {points_to_use} điểm"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()