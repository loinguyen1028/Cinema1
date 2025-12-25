from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Role, User, Room, Seat, Movie, Showtime, Customer, Ticket

DATABASE_URL = "postgresql://cinema_user:cinema_pass@localhost:5432/cinema_db"

class Database:
    def __init__(self):
        self.engine = create_engine(DATABASE_URL, echo=False)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        return self.Session()

    def init_db(self):
        Base.metadata.create_all(self.engine)

db = Database()