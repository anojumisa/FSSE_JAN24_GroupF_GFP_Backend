from flask import Blueprint, request, jsonify
from connectors.mysql_connector import connection, engine
from sqlalchemy.orm import sessionmaker
from models.users import User
from models.products import Products
from models.cart import Cart
from models.cart_item import CartItem

from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_routes = Blueprint('cart_routes', __name__)


@cart_routes.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user_id = get_jwt_identity()
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        cart = session.query(Cart).filter_by(user_id=user_id).first()
        if not cart:
            return jsonify({"message": "Cart not found"}), 404
        
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        items = []
        for item in cart_items:
            product = session.query(Products).filter_by(product_id=item.id).first()
            items.append({
                "product_id": item.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": product.price,
                "total_price": item.quantity * product.price
            })

        return jsonify({"cart_items": items}), 200
    
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to retrieve cart items", "error": str(e)}), 500
    finally:
        session.close()

@cart_routes.route('/cart/add', methods=['POST'])
@jwt_required()
def add_product_to_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        current_user_id = get_jwt_identity()
        data = request.json
        product_id = data.get('productId')
        quantity = data.get('quantity', 1)

        # Debugging statements
        print(f"Received productId: {product_id} of type {type(product_id)}")
        print(f"Received quantity: {quantity} of type {type(quantity)}")

        if product_id is None or product_id == '':
            return jsonify({"message": "productId is required"}), 400

        if isinstance(product_id, str):
            try:
                product_id = int(product_id)
            except ValueError:
                return jsonify({"message": "Invalid productId"}), 400

        if not isinstance(product_id, int):
            return jsonify({"message": "Invalid productId"}), 400

        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"message": "Invalid quantity"}), 400

        # Ensure the user has a cart
        cart = session.query(Cart).filter_by(user_id=current_user_id).first()
        if not cart:
            cart = Cart(user_id=current_user_id)
            session.add(cart)
            session.commit()

        # Check if the item already exists in the cart
        cart_item = session.query(CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            session.add(cart_item)

        session.commit()

        return jsonify({"message": "Product added to cart"}), 200

    except Exception as e:
        session.rollback()
        print(f"Error: {str(e)}")  # Debugging statement
        return jsonify({"message": "An error occurred while adding the product to the cart"}), 500

    finally:
        session.close()

@cart_routes.route('/cart', methods=['GET'])
# @login_required
def view_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Ensure the user has a cart
        cart = session.query(Cart).filter_by(user_id=current_user.id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 200

        # Fetch all items in the cart
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        items = []
        for item in cart_items:
            product = session.query(Products).filter_by(product_id=item.product_id).first()
            items.append({
                "product_id": item.product_id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": product.price,
                "total_price": item.quantity * product.price
            })

        return jsonify({"cart_items": items}), 200

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to retrieve cart items", "error": str(e)}), 500
    finally:
        session.close()

@cart_routes.route('/cart/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_cart_quantity(product_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        current_user_id = get_jwt_identity()
        data = request.json
        quantity = data.get('quantity')

        if not quantity or not isinstance(quantity, int):
            return jsonify({"message": "Invalid quantity"}), 400

        cart = session.query(Cart).filter_by(user_id=current_user_id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 404

        cart_item = session.query(CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            return jsonify({"message": "Product not found in cart"}), 404

        cart_item.quantity = quantity
        session.commit()

        return jsonify({"message": "Cart item updated successfully"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"message": "An error occurred while updating the cart item"}), 500

    finally:
        session.close()

@cart_routes.route('/cart/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_cart_item(product_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        current_user_id = get_jwt_identity()
        cart = session.query(Cart).filter_by(user_id=current_user_id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 200

        cart_item = session.query(CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            return jsonify({"message": "Product not found in cart"}), 404

        session.delete(cart_item)
        session.commit()

        return jsonify({"message": "Cart item removed successfully"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"message": "An error occurred while removing the item"}), 500

    finally:
        session.close()

@cart_routes.route('/cart/checkout', methods=['POST'])
@login_required
def checkout_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Ensure the user has a cart
        cart = session.query(Cart).filter_by(user_id=current_user.id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 200

        # Fetch all items in the cart
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        items = []
        for item in cart_items:
            product = session.query(Products).filter_by(product_id=item.id).first()
            items.append({
                "product_id": item.id,
                "product_name": product.name,
                "quantity": item.quantity,
                "price": product.price,
                "total_price": item.quantity * product.price
            })

        return jsonify({"cart_items": items}), 200

    except SQLAlchemyError as e:    
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to checkout cart", "error": str(e)}), 500
    finally:
        session.close()

@cart_routes.route('/cart/clear', methods=['DELETE'])
@jwt_required()
def clear_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        current_user_id = get_jwt_identity()
        cart = session.query(Cart).filter_by(user_id=current_user_id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 200

        session.query(CartItem).filter_by(cart_id=cart.id).delete()
        session.commit()

        return jsonify({"message": "Cart cleared successfully"}), 200

    except Exception as e:
        session.rollback()
        return jsonify({"message": "An error occurred while clearing the cart"}), 500

    finally:
        session.close()

@cart_routes.route('/cart/total', methods=['GET'])
@login_required
def get_cart_total():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Ensure the user has a cart
        cart = session.query(Cart).filter_by(user_id=current_user.id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 200

        # Fetch all items in the cart
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        total = 0
        for item in cart_items:
            total += item.quantity * item.product.price

        return jsonify({"total": total}), 200

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to get cart total", "error": str(e)}), 500
    finally:
        session.close()

        