from flask import Blueprint, request, jsonify
from connectors.mysql_connector import connection, engine
from sqlalchemy.orm import sessionmaker
from models.users import User
from models.products import Products
from models.cart import Cart
from models.order import Order
from models.order_item import OrderItem
from models.cart_item import CartItem
from models.feedback import Feedback

from sqlalchemy.exc import SQLAlchemyError
from flask_login import current_user, login_required
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_routes = Blueprint('cart_routes', __name__)

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
            # Fetch the product to get the price
            product = session.query(Products).filter_by(id=product_id).first()
            if not product:
                return jsonify({"message": "Product not found"}), 404

            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity,
                price=product.price,  
                user_id=current_user_id

            )
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
@jwt_required()
def view_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get the user ID from the JWT
        user_id = get_jwt_identity()

        # Ensure the user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Retrieve the user's cart
        cart = session.query(Cart).filter_by(user_id=user_id).first()
        if not cart:
            return jsonify({"cart_items": []}), 200  # Empty cart response

        # Retrieve items in the cart
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        items = []

        # Loop through each cart item and get the related product information
        for item in cart_items:
            product = session.query(Products).filter_by(id=item.product_id).first()
            if product:
                items.append({
                    "id": item.id,
                    "product_id": item.product_id,
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "price": product.price,
                    "total_price": item.quantity * product.price,
                    "image_url": product.image_url
                })
            else:
                # If a product related to the cart item is not found
                return jsonify({"message": f"Product with id {item.product_id} not found"}), 404

        session.commit()
        return jsonify({"cart_items": items}), 200

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Querying product with id: {item.product_id}")
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
@jwt_required()
def get_cart_total():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get the user ID from the JWT
        user_id = get_jwt_identity()

        # Ensure the user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Retrieve the user's cart
        cart = session.query(Cart).filter_by(user_id=user_id).first()
        if not cart:
            return jsonify({"total_price": 0}), 200  # Empty cart response

        # Retrieve items in the cart and calculate the total price
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        total_price = 0

        for item in cart_items:
            product = session.query(Products).filter_by(id=item.product_id).first()
            if product:
                total_price += item.quantity * product.price
            else:
                # If a product related to the cart item is not found
                return jsonify({"message": f"Product with id {item.product_id} not found"}), 404

        session.commit()
        return jsonify({"total_price": total_price}), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"message": "Failed to retrieve cart total", "error": str(e)}), 500
    finally:
        session.close()

@cart_routes.route('/cart/checkout', methods=['POST'])
@jwt_required()
def checkout_cart():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get the user ID from the JWT
        user_id = get_jwt_identity()

        # Ensure the user exists
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        # Retrieve the user's cart
        cart = session.query(Cart).filter_by(user_id=user_id).first()
        if not cart:
            return jsonify({"message": "Cart is empty"}), 400

        # Retrieve items in the cart and calculate the total price
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        if not cart_items:
            return jsonify({"message": "Cart is empty"}), 400

        total_price = 0
        order_items = []

        for item in cart_items:
            product = session.query(Products).filter_by(id=item.product_id).first()
            if product:
                total_price += item.quantity * product.price
                order_items.append({
                    "product_id": product.id,
                    "quantity": item.quantity,
                    "price": product.price
                })
            else:
                return jsonify({"message": f"Product with id {item.product_id} not found"}), 404

        # Get payment method from request body
        data = request.get_json()
        if not data or 'payment_method' not in data:
            return jsonify({"message": "Payment method is required"}), 400

        payment_method = data.get('payment_method')

        # Validate payment method
        if payment_method not in ['bank_transfer', 'COD']:
            return jsonify({"message": "Invalid payment method"}), 400

        # Create an order
        order = Order(user_id=user_id, total_price=total_price, payment_method=payment_method)
        session.add(order)
        session.commit()

        # Add order items
        for order_item in order_items:
            new_order_item = OrderItem(
                order_id=order.id,
                product_id=order_item["product_id"],
                quantity=order_item["quantity"],
                price=order_item["price"]
            )
            session.add(new_order_item)

        # Clear the user's cart
        session.query(CartItem).filter_by(cart_id=cart.id).delete()
        session.commit()

        return jsonify({"message": "Checkout successful", "order_id": order.id, "total_price": total_price, "payment_method": payment_method}), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"message": "Failed to checkout", "error": str(e)}), 500
    finally:
        session.close()
    
@cart_routes.route('/order/<int:order_id>/feedback', methods=['POST'])
@jwt_required()
def leave_feedback(order_id):
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Get the user ID from the JWT
        user_id = get_jwt_identity()

        # Ensure the order exists and belongs to the user
        order = session.query(Order).filter_by(id=order_id, user_id=user_id).first()
        if not order:
            return jsonify({"message": "Order not found or does not belong to the user"}), 404

        # Get feedback from request body
        data = request.get_json()
        if not data or 'comment' not in data or 'rating' not in data:  # Check for rating
            return jsonify({"message": "Comment and rating are required"}), 400

        comment_text = data.get('comment')
        rating_value = data.get('rating')

        if rating_value is None:
            return jsonify({"message": "Rating cannot be null"}), 400

        # Create feedback entry
        feedback = Feedback(order_id=order_id, user_id=user_id, rating=rating_value, comment=comment_text)
        session.add(feedback)
        session.commit()

        return jsonify({"message": "Feedback submitted successfully"}), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"message": "Failed to submit feedback", "error": str(e)}), 500
    finally:
        session.close()