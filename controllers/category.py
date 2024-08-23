from flask import Blueprint, request, make_response
from connectors.mysql_connector import connection, engine
from models.products import Category
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user

category_routes = Blueprint("category_routes", __name__)

@category_routes.route('/categories', methods=['POST'])
@login_required
def create_category():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        data = request.json
        new_category = Category(
            name=data['name'],
            description=data.get('description', ''),
            store_id=current_user.id
        )
        
        s.add(new_category)
        s.commit()
        return {"message": "Category created successfully"}, 201

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to create category", "error": str(e)}, 500

@category_routes.route('/categories/<int:category_id>', methods=['GET'])
@login_required
def get_category(category_id):
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        category = s.query(Category).filter(Category.category_id == category_id, Category.store_id == current_user.id).first()
        
        if not category:
            return {"message": "Category not found"}, 404
        
        return {
            "category_id": category.category_id,
            "name": category.name,
            "description": category.description
        }, 200

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to retrieve category", "error": str(e)}, 500

@category_routes.route('/Category/<int:category_id>', methods=['PUT'])
@login_required
def update_category(category_id):
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        category = s.query(Category).filter(Category.category_id == category_id, Category.store_id == current_user.id).first()

        if not category:
            return {"message": "Category not found"}, 404

        data = request.json
        category.name = data['name']
        category.description = data.get('description', '')

        s.commit()
        return {"message": "Category updated successfully"}, 200

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to update category", "error": str(e)}, 500

@category_routes.route('/categories/<int:category_id>', methods=['DELETE'])
@login_required
def delete_category(category_id):
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        category = s.query(Category).filter(Category.category_id == category_id, Category.store_id == current_user.id).first()

        if not category:
            return {"message": "Category not found"}, 404

        s.delete(category)
        s.commit()
        return {"message": "Category deleted successfully"}, 200

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to delete category", "error": str(e)}, 500