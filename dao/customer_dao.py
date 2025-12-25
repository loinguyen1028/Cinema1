from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from db import db
from models import Customer, MembershipTier


class CustomerDAO:
    def get_all(self):
        session = db.get_session()
        try:
            return session.query(Customer) \
                .options(joinedload(Customer.tier)) \
                .filter_by(is_active=True) \
                .order_by(Customer.customer_id.desc()) \
                .all()
        except Exception:
            return []
        finally:
            session.close()

    def get_by_phone(self, phone):
        session = db.get_session()
        try:
            return session.query(Customer) \
                .options(joinedload(Customer.tier)) \
                .filter_by(phone=phone) \
                .first()
        except Exception:
            return None
        finally:
            session.close()

    def get_by_id(self, customer_id):
        session = db.get_session()
        try:
            return session.query(Customer) \
                .options(joinedload(Customer.tier)) \
                .filter_by(customer_id=customer_id) \
                .first()
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

    def get_tier_id_by_points(self, session, points):
        tier = session.query(MembershipTier) \
            .filter(MembershipTier.min_point <= points) \
            .order_by(MembershipTier.min_point.desc()) \
            .first()
        return tier.id if tier else 1

    def add(self, name, phone, email, dob, points, level):
        session = db.get_session()
        try:
            if session.query(Customer).filter_by(phone=phone).first():
                return False, f"Số điện thoại {phone} đã tồn tại trong hệ thống!"

            if email and email.strip():
                exists_email = session.query(Customer) \
                    .filter(Customer.email == email.strip()) \
                    .first()
                if exists_email:
                    return False, f"Email '{email}' đã được sử dụng bởi khách hàng khác!"

            points_val = int(points) if str(points).isdigit() else 0
            tier_id = self.get_tier_id_by_points(session, points_val)

            new_cus = Customer(
                name=name,
                phone=phone,
                email=email,
                points=points_val,
                tier_id=tier_id,
                extra_info={"dob": dob}
            )

            session.add(new_cus)
            session.commit()
            return True, "Thêm khách hàng thành công!"

        except IntegrityError:
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

            exist_phone = session.query(Customer).filter(
                Customer.phone == phone,
                Customer.customer_id != customer_id
            ).first()

            if exist_phone:
                return False, f"Số điện thoại {phone} đang thuộc về khách hàng: {exist_phone.name}"

            if email and email.strip():
                exist_email = session.query(Customer).filter(
                    Customer.email == email.strip(),
                    Customer.customer_id != customer_id
                ).first()
                if exist_email:
                    return False, f"Email '{email}' đang thuộc về khách hàng: {exist_email.name}"

            cus.name = name
            cus.phone = phone
            cus.email = email

            points_val = int(points) if str(points).isdigit() else 0
            cus.points = points_val
            cus.tier_id = self.get_tier_id_by_points(session, points_val)

            extra = dict(cus.extra_info) if cus.extra_info else {}
            extra["dob"] = dob
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

            cus.is_active = False
            session.commit()
            return True, "Đã xóa khách hàng thành công!"

        except Exception as e:
            session.rollback()
            return False, f"Lỗi khi xóa: {str(e)}"
        finally:
            session.close()

    def update_membership(self, customer_id, amount_paid):
        session = db.get_session()
        try:
            cus = session.query(Customer).get(customer_id)
            if not cus:
                return False, "Khách hàng không tồn tại"

            points_added = int(amount_paid / 10000)
            cus.points += points_added
            cus.tier_id = self.get_tier_id_by_points(session, cus.points)

            tier_name = session.query(MembershipTier.tier_name) \
                .filter_by(id=cus.tier_id) \
                .scalar()

            session.commit()
            return True, f"Cộng {points_added} điểm. Hạng hiện tại: {tier_name}"

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

            current_points = cus.points or 0
            if current_points < points_to_use:
                return False, f"Không đủ điểm (Có: {current_points})"

            cus.points -= points_to_use
            cus.tier_id = self.get_tier_id_by_points(session, cus.points)

            session.commit()
            return True, f"Đã trừ {points_to_use} điểm"

        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()
