from models.base import Base
from sqlalchemy import Integer, String, Text, Numeric, DateTime, Column, ForeignKey, Table, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Step 1: Define the Category model
class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    store_id = Column(Integer, ForeignKey('store.id'), nullable=False)
    products = relationship('ProductCategory', back_populates='category')

# Step 2: Define the ProductCategory association table
class ProductCategory(Base):
    __tablename__ = 'product_categories'

    id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('categories.id'), primary_key=True)
    product = relationship('Products', back_populates='categories')
    category = relationship('Category', back_populates='products')

# Step 3: Update the Products model
class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)  # Ensure consistency with DB
    stock_quantity = Column(Integer, nullable=False)
    image_url = Column(String(255))
    location = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.current_timestamp())
    featured = Column(Boolean, default=False)  # Changed to Boolean for clarity
    store_id = Column(Integer, ForeignKey('store.id'), nullable=False)

    store = relationship("Stores", back_populates="products")
    categories = relationship('ProductCategory', back_populates='product')
    order_items = relationship('OrderItem', back_populates='product')
    cart_items = relationship('CartItem', back_populates='product')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock_quantity': self.stock_quantity,
            'image_url': self.image_url,
            'location': self.location,
            'featured': self.featured,
            'store_id': self.store_id
        }