from models.base import Base
from sqlalchemy import Integer, String, Text, Numeric, DateTime, Column, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Products(Base):
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    image_url = Column(String(255))
    location = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    store_id = Column(Integer, ForeignKey('store.id'), nullable=False)
    store = relationship("Stores", back_populates="products")



