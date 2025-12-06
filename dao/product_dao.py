from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from db import db
from models import Product


class ProductDAO:
    def get_all(self):
        session = db.get_session()
        try:
            return session.query(Product).filter_by(is_active=True).order_by(Product.category).all()
        finally:
            session.close()

    def add(self, name, category, price, image_path=""):
        session = db.get_session()
        try:
            new_prod = Product(name=name, category=category, price=price, image_path=image_path)
            session.add(new_prod)
            session.commit()
            # --- SỬA LỖI: Thêm thông báo vào sau True ---
            return True, "Thêm sản phẩm thành công"
        except SQLAlchemyError as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def update(self, p_id, name, category, price, image_path=""):
        session = db.get_session()
        try:
            prod = session.query(Product).get(p_id)
            if prod:
                prod.name = name
                prod.category = category
                prod.price = price
                if image_path:
                    prod.image_path = image_path
                session.commit()
                # --- SỬA LỖI: Thêm thông báo ---
                return True, "Cập nhật thành công"

            # --- SỬA LỖI: Thêm thông báo ---
            return False, "Không tìm thấy sản phẩm để sửa"
        except SQLAlchemyError as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def delete(self, p_id):
        session = db.get_session()
        try:
            prod = session.query(Product).get(p_id)
            if prod:
                prod.is_active = False # Xóa mềm
                session.commit()
                return True, "Đã xóa sản phẩm"
            return False, "Không tìm thấy"
        except SQLAlchemyError as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def get_by_id(self, p_id):
        session = db.get_session()
        try:
            return session.query(Product).get(p_id)
        finally:
            session.close()

    def search_products(self, keyword="", category="Tất cả"):
        session = db.get_session()
        try:
            query = session.query(Product).filter_by(is_active=True)

            # Lọc theo từ khóa (Tên sản phẩm)
            if keyword:
                query = query.filter(Product.name.ilike(f"%{keyword}%"))

            # Lọc theo loại
            if category and category != "Tất cả":
                query = query.filter(Product.category == category)

            return query.order_by(Product.name).all()
        finally:
            session.close()

    def get_categories(self):
        """Lấy danh sách các loại sản phẩm duy nhất đang có"""
        session = db.get_session()
        try:
            # Lấy distinct category
            cats = session.query(Product.category).filter_by(is_active=True).distinct().all()
            return [c[0] for c in cats]
        finally:
            session.close()