from flask import Blueprint, jsonify, make_response, request
from connectors.mysql_connector import engine
from models.users import User
from sqlalchemy.orm import sessionmaker
from flask_login import login_user, login_required, logout_user, current_user
from flask_jwt_extended import create_access_token, jwt_required

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

@user_routes.route('/profile', methods=['GET'])
@login_required
def get_user_profile():
    return jsonify({ 
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "address": current_user.address,
        "city": current_user.city,
        "state": current_user.state,
        "zip_code": current_user.zip_code,
        "image_url": current_user.image_url
    })

@user_routes.route('/profile', methods=['PUT'])
@login_required
def update_user_profile():
    session = Session()

    try:
        data = request.get_json()
        if not data or not isinstance(data, dict):
            return jsonify({"message": "Invalid data provided"}), 400

        required_fields = [
            'first_name', 'last_name', 'address', 'city',
            'state', 'zip_code', 'image_url'
        ]

        for field in required_fields:
            if field not in data:
                return jsonify({"message": f"{field.replace('_', ' ').title()} is required"}), 400

        user = session.query(User).filter(User.id == current_user.id).first()

        if not user:
            return jsonify({"message": "User not found"}), 404

        user.first_name = data['first_name']
        user.last_name = data['last_name']
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

@user_routes.route('/login', methods=['POST'])
def check_login_jwt():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        data = request.json 
        email = data['email']

        user = s.query(User).filter(User.email == email).first()                

        if user == None:
            return { "message": "User not found" }, 403
        
        if not user.check_password(request.json['password']):
            return { "message": "Invalid password" }, 403

        access_token = create_access_token(identity=user.id, additional_claims= {"username": user.username, "id": user.id})

        return {
            "access_token": access_token,
            "message": "Login Success"
        }, 200        

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return { "message": "Login Failed" }, 500        

@user_routes.route('/logout', methods=['POST'])
# @login_required
@jwt_required()
def user_logout():
    logout_user()
    return jsonify({"message": "Logout Success"})