from flask import Blueprint, request, jsonify
from connectors.mysql_connector import connection, engine
from sqlalchemy.orm import sessionmaker
from models.users import User
from models.products import Products
from models.cart import Cart
from models.cart_item import CartItem

from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user, login_required

cart_routes = Blueprint('cart_routes', __name__)

@cart_routes.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)  # Default to 1 if not provided

        # Fetch the product
        product = session.query(Products).filter_by(product_id=product_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404

        # Ensure the user has a cart
        cart = session.query(Cart).filter_by(user_id=current_user.id).first()
        if not cart:
            cart = Cart(user_id=current_user.id)
            session.add(cart)
            session.commit()

        # Check if the product is already in the cart
        cart_item = session.query(CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
        if cart_item:
            # Update the quantity if the product already exists in the cart
            cart_item.quantity += quantity
        else:
            # Add a new item to the cart
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            session.add(cart_item)

        # Commit the transaction
        session.commit()

        return jsonify({"message": "Product added to cart successfully"}), 201

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to add product to cart", "error": str(e)}), 500

    finally:
        session.close()


@cart_routes.route('/cart/view', methods=['GET'])
@login_required
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

@cart_routes.route('/cart/update', methods=['PUT'])
@login_required
def update_cart_item():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        data = request.json
        product_id = data.get('product_id')
        quantity = data.get('quantity')

        if not product_id or not isinstance(product_id, int):
            return jsonify({"message": "Invalid product_id"}), 400
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"message": "Invalid quantity"}), 400

        # Ensure the user has a cart
        cart = session.query(Cart).filter_by(user_id=current_user.id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 200

        # Fetch the cart item
        cart_item = session.query(CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            return jsonify({"message": "Product not found in cart"}), 404

        # Update the quantity
        cart_item.quantity = quantity
        session.commit()

        return jsonify({"message": "Cart item updated successfully"}), 200

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to update cart item", "error": str(e)}), 500
    finally:
        session.close()

@cart_routes.route('/cart/remove', methods=['DELETE'])
@login_required
def remove_cart_item():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        data = request.json
        product_id = data.get('product_id')

        if not product_id or not isinstance(product_id, int):
            return jsonify({"message": "Invalid product_id"}), 400

        # Ensure the user has a cart
        cart = session.query(Cart).filter_by(user_id=current_user.id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 200

        # Fetch the cart item
        cart_item = session.query(CartItem).filter_by(cart_id=cart.id, product_id=product_id).first()
        if not cart_item:
            return jsonify({"message": "Product not found in cart"}), 404

        # Remove the cart item
        session.delete(cart_item)
        session.commit()

        return jsonify({"message": "Cart item removed successfully"}), 200

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to remove cart item", "error": str(e)}), 500
    finally:
        session.close()
