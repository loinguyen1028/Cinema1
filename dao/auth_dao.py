from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload  # <--- QUAN TRỌNG: Phải import cái này
from db import db
from models import User


class AuthDAO:
    def login(self, username, password):
        session = db.get_session()
        try:
            # SỬA LỖI TẠI ĐÂY: Thêm .options(joinedload(User.role))
            # Để lấy luôn thông tin Role cùng với User trước khi đóng session
            user = session.query(User).options(joinedload(User.role)).filter_by(username=username).first()

            if user and user.password == password:
                return user
            return None
        except Exception as e:
            print(f"Login Error: {e}")
            return None
        finally:
            session.close()

    def get_user_by_id(self, user_id):
        session = db.get_session()
        try:
            # Cũng nên thêm joinedload ở đây nếu sau này cần dùng role
            return session.query(User).options(joinedload(User.role)).get(user_id)
        except Exception:
            return None
        finally:
            session.close()

    def change_password(self, user_id, new_pass):
        session = db.get_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                user.password = new_pass
                session.commit()
                return True
            return False
        except SQLAlchemyError:
            session.rollback()
            return False
        finally:
            session.close()