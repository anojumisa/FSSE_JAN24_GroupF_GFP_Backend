from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total_price = Column(Integer, nullable=False)
    payment_method = Column(String(50), nullable=False)
    delivery_option = Column(String, nullable=False)
    status = Column(String(50), default='pending')
    review = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')
    feedback = relationship('Feedback', back_populates='order')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_price': self.total_price,
            'payment_method': self.payment_method,
            'delivery_option': self.delivery_option,
            'status': self.status,
            'review': self.review,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'order_items': [item.to_dict() for item in self.order_items]
        }
    