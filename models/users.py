from models.base import Base

from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin

import bcrypt

class User(Base, UserMixin):
    __tablename__ = 'users'

    user_id = mapped_column(Integer, primary_key=True, autoincrement=True)
    username = mapped_column(String(50), nullable=False)
    email = mapped_column(String(100), nullable=False)
    password_hash = mapped_column(String(255), nullable=False)
    first_name = mapped_column(String(50), nullable=False)
    last_name = mapped_column(String(50), nullable=False)
    address = mapped_column(String(255), nullable=False)
    city = mapped_column(String(100), nullable=False)
    state = mapped_column(String(100), nullable=False)
    zip_code = mapped_column(String(20), nullable=False)
    image_url = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())

    def set_password(self, password_hash):
        self.password_hash = bcrypt.hashpw(password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password_hash):
        return bcrypt.checkpw(password_hash.encode('utf-8'), self.password_hash.encode('utf-8'))