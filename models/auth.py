from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base 

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True)
    role_name = Column(String(20), unique=True, nullable=False)
    

    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    full_name = Column(String(100))
    role_id = Column(Integer, ForeignKey('roles.role_id'), nullable=False)

    role = relationship("Role", back_populates="users")
    sales = relationship("Ticket", back_populates="user")