from models.base import Base

from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column, relationship
from flask_login import UserMixin

import bcrypt

class User(Base, UserMixin):
    __tablename__ = 'users'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(50), nullable=False)
    email = mapped_column(String(100), nullable=False, unique=True)
    password = mapped_column(String(255), nullable=False)
    first_name = mapped_column(String(50), nullable=False)
    last_name = mapped_column(String(50), nullable=False)
    address = mapped_column(String(255), nullable=True)
    city = mapped_column(String(100), nullable=True)
    state = mapped_column(String(100), nullable=True)
    zip_code = mapped_column(String(20), nullable=True)
    image_url = mapped_column(String(255), nullable=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())

    carts = relationship('Cart', back_populates='user', lazy=True)
    # cart_items = relationship('CartItem', back_populates='user', lazy=True)
    orders = relationship('Order', back_populates='user')
    feedback = relationship('Feedback', back_populates='user')

    def set_password(self, password):
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))