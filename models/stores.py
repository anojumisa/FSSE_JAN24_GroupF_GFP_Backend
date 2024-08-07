from models.base import Base

from sqlalchemy.sql import func
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import mapped_column
from flask_login import UserMixin

import bcrypt

class Stores(Base, UserMixin):
    __tablename__ = 'store'

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_full_name = mapped_column(String(50), nullable=False)
    email = mapped_column(String(100), nullable=False)
    password_hash = mapped_column(String(100), nullable=False)
    username = mapped_column(String(50), nullable=False)
    store_name = mapped_column(String(100), nullable=False)
    description = mapped_column(String(255), nullable=False)
    image_url = mapped_column(String(255), nullable=False)
    bank_account = mapped_column(String(20), nullable=False)
    contact_number = mapped_column(String(15), nullable=False)
    address = mapped_column(String(255), nullable=False)
    city = mapped_column(String(100), nullable=False)
    state = mapped_column(String(100), nullable=False)
    zip_code = mapped_column(String(20), nullable=False)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    def set_password(self, password_hash):
        self.password_hash = bcrypt.hashpw(password_hash.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password_hash):
        return bcrypt.checkpw(password_hash.encode('utf-8'), self.password_hash.encode('utf-8'))