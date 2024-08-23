from flask import request, jsonify, Blueprint
from connectors.mysql_connector import connection, engine
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import Schema, fields, ValidationError, validate
from models.users import User 
from models.order import Order
from models.cart_item import CartItem
from models.cart import Cart
from models.products import Products
from models.order_item import OrderItem, OrderItemSchema
from sqlalchemy.orm import sessionmaker
from datetime import datetime  # Add this line to import the datetime module

import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderSchema(Schema):
    payment_method = fields.Str(required=True)
    delivery_option = fields.Str(required=True)
    total = fields.Float(required=True)
    status = fields.Str(required=True)
    total_price = fields.Float(required=True)

order_routes = Blueprint("order_routes", __name__)

@order_routes.route('/order_items', methods=['POST'])
def create_order_item():
    schema = OrderItemSchema()
    try:
        order_items_data = request.json
        created_order_items = []

        for item_data in order_items_data:
            order_item_data = schema.load(item_data)
            if 'order_id' not in order_item_data:
                return jsonify({"message": "Missing 'order_id' in order item data"}), 400

            order_item = OrderItem(
                product_id=order_item_data["product_id"],
                quantity=order_item_data["quantity"],
                price=order_item_data["price"],
                order_id=order_item_data["order_id"]
            )

            created_order_items.append(order_item)

        session = connection()
        session.add_all(created_order_items)
        session.commit()
        session.close()

        return jsonify({"message": "Order items created successfully", "order_items": [item.to_dict() for item in created_order_items]}), 201

    except ValidationError as err:
        return jsonify({"message": "Invalid data provided", "errors": err.messages}), 400
    except SQLAlchemyError as e:
        session.rollback()
        session.close()
        return jsonify({"message": "Database error", "error": str(e)}), 500
    except Exception as e:
        return jsonify({"message": "An unexpected error occurred", "error": str(e)}), 500
      
@order_routes.route("/create_order", methods=["POST"])
@jwt_required()
def create_order():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user_id = get_jwt_identity()
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        data = request.get_json()
        if data is None:
            return jsonify({"message": "Invalid data provided"}), 400

        # Validate input data
        try:
            order_data = OrderSchema().load(data)
        except ValidationError as err:
            return jsonify({"message": "Invalid data provided", "errors": err.messages}), 400

        order = Order(
            user_id=user_id,
            payment_method=order_data["payment_method"],
            delivery_option=order_data["delivery_option"],
            total_price=order_data["total_price"],
            status=order_data.get("status", "pending"),
            review=order_data.get("review", None),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        session.add(order)
        session.flush()  # Flush to get the order ID

        # Associate the cart items with the order
        cart_items = session.query(CartItem).filter_by(user_id=user_id).all()
        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
            session.add(order_item)

        # Clear the user's cart
        session.query(CartItem).filter_by(user_id=user_id).delete()
        session.commit()

        return jsonify({"message": "Order created successfully", "order": order.to_dict()}), 201
    
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Error: {str(e)}")
        return jsonify({"message": "Failed to create order", "error": str(e)}), 500
    finally:
        session.close()
@order_routes.route("/order", methods=["GET"])
@jwt_required()
def get_orders():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user_id = get_jwt_identity()
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404

        orders = session.query(Order).filter_by(user_id=user_id).all()
        orders_data = [order.to_dict() for order in orders]

        return jsonify(orders_data), 200

    except SQLAlchemyError as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"message": "Failed to retrieve orders", "error": str(e)}), 500
    finally:
        session.close()

@order_routes.route('/checkout', methods=['POST'])
@jwt_required()
def checkout(): 
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

        # Retrieve items in the cart
        cart_items = session.query(CartItem).filter_by(cart_id=cart.id).all()
        if not cart_items:
            return jsonify({"message": "Cart is empty"}), 400

        # Calculate the total price
        total_price = 0
        for item in cart_items:
            product = session.query(Products).filter_by(id=item.product_id).first()
            if product:
                total_price += item.quantity * product.price
            else:
                return jsonify({"message": f"Product with id {item.product_id} not found"}), 404

        # Create a new order
        new_order = Order(user_id=user_id, total_price=total_price, status="Pending")
        session.add(new_order)
        session.commit()

        # Create order items
        for item in cart_items:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.quantity * product.price
            )
            session.add(order_item)

        # Clear the user's cart
        session.query(CartItem).filter_by(cart_id=cart.id).delete()
        session.commit()

        return jsonify({"message": "Checkout successful", "order_id": new_order.id}), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({"message": "Checkout failed", "error": str(e)}), 500
    finally:
        session.close()