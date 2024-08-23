from flask import Blueprint, jsonify, request
from connectors.mysql_connector import engine
from models.users import User
from models.order import Order 
from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

user_routes = Blueprint("user_routes", __name__)
Session = sessionmaker(bind=engine)

@user_routes.route('/register', methods=['POST'])
def register_user():
    session = Session()

    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"message": "Invalid data provided"}), 400

        required_fields = [
            'username', 'email', 'password',
            'first_name', 'last_name', 'address', 'city',
            'state', 'zip_code', 'image_url'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"{field.replace('_', ' ').title()} is required"}), 400

        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            image_url=data.get('image_url')
        )

        password = data.get('password')
        new_user.set_password(password)

        session.add(new_user)
        session.commit()
        return jsonify({"message": "Register Success"}), 200

    except Exception as e:
        session.rollback()
        print(f"Exception: {e}")
        return jsonify({"message": "Failed to Register"}), 500

    finally:
        session.close()

@user_routes.route('/login', methods=['POST'])
def check_login():
    session = Session()

    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({"message": "Invalid credentials"}), 400

        user = session.query(User).filter(User.email == data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({"message": "Invalid email or password"}), 403

        # Create a JWT token
        access_token = create_access_token(identity=user.id, additional_claims={
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        })
        return jsonify({"access_token": access_token, "message": "Login Success"}), 200

    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({"message": "Login Failed"}), 500

    finally:
        session.close()

@user_routes.route('/user/dashboard', methods=['GET'])
@jwt_required()
def get_user_dashboard_data():
    session = Session()

    try:
        user_id = get_jwt_identity()
        user = session.query(User).filter_by(id=user_id).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        transactions = session.query(Order).filter_by(user_id=user_id).all()

        data = {
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "address": user.address,
                "city": user.city,
                "state": user.state,
                "zip_code": user.zip_code,
                "image_url": user.image_url,
                "created_at": user.created_at,
                "username": user.username
            },
            "transactions": [
                {
                    "id": transaction.id,
                    "total_price": transaction.total_price,
                    "payment_method": transaction.payment_method,
                    "status": transaction.status,
                    "created_at": transaction.created_at
                } for transaction in transactions
            ]
        }
        return jsonify(data), 200

    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        return jsonify({"message": "Failed to fetch user data"}), 500

    finally:
        session.close()

@user_routes.route('/profile', methods=['PUT'])
@jwt_required()
def update_user_profile():
    session = Session()

    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"message": "Invalid data provided"}), 400

        required_fields = [
            'first_name', 'last_name', 'address', 'email', 'city',
            'state', 'zip_code', 'image_url'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"{field.replace('_', ' ').title()} is required"}), 400

        user_id = get_jwt_identity()
        user = session.query(User).filter(User.id == user_id).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.address = data['address']
        user.city = data['city']
        user.state = data['state']
        user.zip_code = data['zip_code']
        user.image_url = data['image_url']

        session.commit()
        return jsonify({"message": "Update Success"}), 200

    except Exception as e:
        print(e)
        session.rollback()
        return jsonify({"message": "Update Failed"}), 500

    finally:
        session.close()

@user_routes.route('/logout', methods=['POST'])
@jwt_required()
def user_logout():
    return jsonify({"message": "Logout Success"}), 200
