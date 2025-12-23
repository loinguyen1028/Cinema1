from sqlalchemy.exc import IntegrityError
from db import db
from models import MembershipTier


class TierDAO:
    def get_all(self):
        session = db.get_session()
        try:
            # Sắp xếp theo điểm tăng dần để dễ nhìn
            return session.query(MembershipTier).order_by(MembershipTier.min_point.asc()).all()
        finally:
            session.close()

    def get_by_id(self, tier_id):
        session = db.get_session()
        try:
            return session.query(MembershipTier).get(tier_id)
        finally:
            session.close()

    def add(self, name, min_point, discount):
        session = db.get_session()
        try:
            # Kiểm tra trùng tên hạng
            if session.query(MembershipTier).filter_by(tier_name=name).first():
                return False, f"Tên hạng '{name}' đã tồn tại!"

            new_tier = MembershipTier(
                tier_name=name,
                min_point=min_point,
                discount_percent=discount
            )
            session.add(new_tier)
            session.commit()
            return True, "Thêm hạng mới thành công!"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            session.close()

    def update(self, tier_id, name, min_point, discount):
        session = db.get_session()
        try:
            tier = session.query(MembershipTier).get(tier_id)
            if not tier:
                return False, "Không tìm thấy hạng cần sửa!"

            # Kiểm tra trùng tên với hạng khác
            exist = session.query(MembershipTier).filter(
                MembershipTier.tier_name == name,
                MembershipTier.id != tier_id
            ).first()
            if exist:
                return False, f"Tên hạng '{name}' đã được sử dụng!"

            tier.tier_name = name
            tier.min_point = min_point
            tier.discount_percent = discount

            session.commit()
            return True, "Cập nhật thành công!"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi hệ thống: {str(e)}"
        finally:
            session.close()

    def delete(self, tier_id):
        session = db.get_session()
        try:
            tier = session.query(MembershipTier).get(tier_id)
            if not tier:
                return False, "Không tìm thấy hạng!"

            # Lưu ý: Nếu database có ràng buộc khóa ngoại (Foreign Key),
            # việc xóa hạng đang có người dùng sẽ gây lỗi.
            # Cần xử lý Exception IntegrityError ở đây.

            session.delete(tier)
            session.commit()
            return True, "Xóa hạng thành công!"
        except IntegrityError:
            session.rollback()
            return False, "Không thể xóa hạng đang có thành viên sử dụng!"
        except Exception as e:
            session.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            session.close()