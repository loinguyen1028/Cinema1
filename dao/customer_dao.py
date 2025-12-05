from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import Customer


class CustomerDAO:
    def get_all(self):
        session = db.get_session()
        try:
            return session.query(Customer).order_by(Customer.customer_id.desc()).all()
        finally:
            session.close()

    def search(self, keyword):
        session = db.get_session()
        try:
            # Tìm theo Tên hoặc Số điện thoại
            return session.query(Customer).filter(
                (Customer.name.ilike(f"%{keyword}%")) |
                (Customer.phone.ilike(f"%{keyword}%"))
            ).order_by(Customer.customer_id.desc()).all()
        finally:
            session.close()

    def get_by_id(self, customer_id):
        session = db.get_session()
        try:
            return session.query(Customer).get(customer_id)
        finally:
            session.close()

    def add(self, name, phone, email, dob, points, level):
        session = db.get_session()
        try:
            # Gom thông tin phụ vào JSON
            info = {
                "dob": dob,
                "points": int(points) if points else 0,
                "level": level
            }
            new_cus = Customer(name=name, phone=phone, email=email, extra_info=info)
            session.add(new_cus)
            session.commit()
            return True
        except SQLAlchemyError as e:
            print(f"Lỗi thêm khách hàng: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def update(self, customer_id, name, phone, email, dob, points, level):
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if cus:
                cus.name = name
                cus.phone = phone
                cus.email = email

                # Update JSON
                current_info = dict(cus.extra_info) if cus.extra_info else {}
                current_info["dob"] = dob
                current_info["points"] = int(points) if points else 0
                current_info["level"] = level
                cus.extra_info = current_info

                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            print(f"Lỗi sửa khách hàng: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def delete(self, customer_id):
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if cus:
                session.delete(cus)
                session.commit()
                return True
            return False
        except SQLAlchemyError:
            session.rollback()
            return False
        finally:
            session.close()

    def get_by_phone(self, phone):
        """Tìm khách hàng theo SĐT"""
        session = db.get_session()
        try:
            return session.query(Customer).filter_by(phone=phone).first()
        finally:
            session.close()

    def update_membership(self, customer_id, amount_paid):
        """
        Cộng điểm và tự động cập nhật hạng thành viên
        Quy tắc: 10,000 VND = 1 điểm
        """
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if cus:
                # 1. Tính điểm cộng thêm
                points_added = int(amount_paid / 10000)

                # 2. Lấy dữ liệu cũ
                current_info = dict(cus.extra_info) if cus.extra_info else {}
                current_points = current_info.get("points", 0)

                # 3. Cộng dồn điểm
                new_points = current_points + points_added

                # 4. Logic thăng hạng (Level Up)
                new_level = "Thân thiết"
                if new_points >= 2000:
                    new_level = "Kim cương"
                elif new_points >= 1000:
                    new_level = "Vàng"
                elif new_points >= 500:
                    new_level = "Bạc"

                # Cập nhật vào JSON
                current_info["points"] = new_points
                current_info["level"] = new_level

                cus.extra_info = current_info
                session.commit()

                return True, f"Cộng {points_added} điểm. Hạng hiện tại: {new_level}"
            return False, "Không tìm thấy khách hàng"
        except Exception as e:
            session.rollback()
            print(f"Lỗi update member: {e}")
            return False, str(e)
        finally:
            session.close()