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