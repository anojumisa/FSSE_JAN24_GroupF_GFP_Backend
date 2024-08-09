from flask import Blueprint, request, make_response
from connectors.mysql_connector import connection, engine
from models.products import Products, Category, ProductCategory
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user

product_routes = Blueprint('product_routes', __name__)

@product_routes.route('/product/<int:product_id>/categories', methods=['POST'])
@login_required
def add_product_categories(product_id):
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        product = s.query(Products).filter(Products.product_id == product_id).first()
        if not product:
            return {"message": "Product not found"}, 404

        data = request.json
        category_ids = data.get('category_ids', [])
        categories = s.query(Category).filter(Category.category_id.in_(category_ids)).all()

        for category in categories:
            product_category = ProductCategory(product_id=product.product_id, category_id=category.category_id)
            s.add(product_category)

        s.commit()
        return {"message": "Categories added to product successfully"}, 200

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to add categories to product", "error": str(e)}, 500
    
    finally:
        s.close()

@product_routes.route('/product/<int:product_id>/categories', methods=['DELETE'])
@login_required
def remove_product_categories(product_id):
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        product = s.query(Products).filter(Products.product_id == product_id).first()
        if not product:
            return {"message": "Product not found"}, 404

        data = request.json
        category_ids = data.get('category_ids', [])
        categories = s.query(Category).filter(Category.category_id.in_(category_ids)).all()

        for category in categories:
            if category in product.categories:
                product.categories.remove(category)

        s.commit()
        return {"message": "Categories removed from product successfully"}, 200

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to remove categories from product", "error": str(e)}, 500