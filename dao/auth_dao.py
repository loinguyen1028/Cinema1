from sqlalchemy.orm import joinedload
from db import db
from models import User

class AuthDAO:
    def login(self, username, password):
        session = db.get_session()
        try:
            user = session.query(User).options(joinedload(User.role)).filter_by(username=username).first()

            if user and user.password == password:
                return user
            else:
                return None
        except Exception as e:
            print(f"Lỗi DAO Login: {e}")
            return None
        finally:
            session.close()

    def get_user_by_id(self, user_id):
        session = db.get_session()
        try:
            return session.query(User).get(user_id)
        finally:
            session.close()

    def change_password(self, user_id, new_password):
        session = db.get_session()
        try:
            user = session.query(User).get(user_id)
            if user:
                user.password = new_password
                session.commit()
                return True
            return False
        except SQLAlchemyError:
            session.rollback()
            return False
        finally:
            session.close()