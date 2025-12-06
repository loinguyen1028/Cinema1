from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Product(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50))
    price = Column(Numeric(10, 2), nullable=False)
    image_path = Column(String(255))
    is_active = Column(Boolean, default=True)

    ticket_products = relationship("TicketProduct", back_populates="product")

    def __repr__(self):
        return f"<Product({self.name})>"