from models.base import Base
from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, relationship

class Feedback(Base):
    __tablename__ = 'feedback'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_id = mapped_column(Integer, ForeignKey('orders.id'), nullable=False)
    user_id = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    rating = mapped_column(Integer, nullable=False)
    comment = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='feedback')
    order = relationship('Order', back_populates='feedback')