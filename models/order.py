from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from datetime import datetime
from models.base import Base

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total = Column(Integer, nullable=False)
    payment_method = Column(String(50), nullable=False)
    status = Column(String(50), default='pending')
    review = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship('User', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status,
            'review': self.review,
            'total': self.total,
            'payment_method': self.payment_method,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            # Add other fields as necessary
        }