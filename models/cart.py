from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base  

class Cart(Base):
    __tablename__ = 'carts'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='carts')
    cart_items = relationship('CartItem', back_populates='cart', cascade='all, delete-orphan')



    