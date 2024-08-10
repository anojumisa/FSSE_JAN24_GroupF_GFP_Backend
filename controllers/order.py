from flask import Blueprint, request, make_response, jsonify
from connectors.mysql_connector import connection, engine
from models.users import User
from models.products import Products
from models.order import Order
from models.order_item import OrderItem
from sqlalchemy.orm import sessionmaker
from flask_login import login_required, current_user
from sqlalchemy.exc import SQLAlchemyError

order_routes = Blueprint("order_routes", __name__)

@order_routes.route('/orders', methods=['GET'])
@login_required
def get_orders():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter_by(id=current_user.id).first()
        orders = session.query(Order).filter_by(user_id=user.id).all()
        
        # Convert orders to a list of dictionaries
        orders_list = [order.to_dict() for order in orders]

        return jsonify(orders_list), 200
    except SQLAlchemyError as e:
        return make_response(jsonify({"error": str(e)}), 500)
    finally:
        session.close()


@order_routes.route('/order', methods=['POST'])
@login_required
def create_order():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        user = session.query(User).filter_by(id=current_user.id).first()
        order = Order(user_id=user.id, total=0, payment_method="Cash on Delivery")
        session.add(order)
        session.commit()

        return jsonify({"message": "Order created successfully", "order_id": order.id}), 200
    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to create order", "error": str(e)}), 500
    finally:
        session.close()

@order_routes.route('/order/add', methods=['POST'])
@login_required
def add_to_order():
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

        # Fetch the order
        order = session.query(Order).filter_by(user_id=current_user.id).first()
        if not order:
            # Create a new order if it doesn't exist
            order = Order(user_id=current_user.id, total=0, status='pending')
            session.add(order)
            session.commit()

        # Check if the product is already in the cart
        order_item = session.query(OrderItem).filter_by(order_id=order.id, product_id=product_id).first()
        if order_item:
            # Update the quantity if the product already exists in the cart
            order_item.quantity += quantity
        else:
            # Add a new item to the cart
            order_item = OrderItem(order_id=order.id, product_id=product_id, quantity=quantity, price=product.price)
            session.add(order_item)

        # Recalculate the total
        order.total = sum(item.quantity * item.price for item in session.query(OrderItem).filter_by(order_id=order.id).all())

        # Commit the transaction
        session.commit()

        return jsonify({"message": "Product added to order successfully"}), 201

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error: {str(e)}")
        return jsonify({"message": "Failed to add product to order", "error": str(e)}), 500

    finally:
        session.close()
