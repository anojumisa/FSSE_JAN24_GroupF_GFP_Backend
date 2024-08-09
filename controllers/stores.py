from flask import Blueprint, jsonify, make_response, request
from connectors.mysql_connector import connection, engine
from models.stores import Stores
from models.products import Products

from sqlalchemy.orm import sessionmaker

from flask_login import login_user, login_required, logout_user, current_user

store_routes = Blueprint("store_routes", __name__)

@store_routes.route('/store_register', methods=['POST'])
def register_seller():
    Session = sessionmaker(connection)
    s = Session()
    s.begin()

    data = request.get_json()
    if data is None or not isinstance(data, dict):
        return jsonify({"message": "Invalid data provided"}), 400

    required_fields = [
        'seller_full_name', 'username', 'email', 'store_name',
        'description', 'bank_account', 'contact_number', 'image_url',
        'address', 'city', 'state', 'zip_code', 'password_hash'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({"message": f"{field.replace('_', ' ').title()} is required"}), 400

    try:

        data = request.get_json()
             
        NewSeller = Stores(
            seller_full_name=data.get('seller_full_name'),
            username=data.get('username'),
            email=data.get('email'),
            store_name=data.get('store_name'),
            description=data.get('description'),
            bank_account=data.get('bank_account'),
            contact_number=data.get('contact_number'),
            image_url=data.get('image_url'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code')           
        )
        
        password_hash = data.get('password_hash')
        if password_hash is None:
            raise ValueError("Password cannot be None")
        NewSeller.set_password(password_hash)
        
        s.add(NewSeller)
        s.commit()

    except Exception as e:
        print(e)
        s.rollback()
        return { "message": "Register Failed"}, 500
    
    return { "message": "Register Success" }, 200

@store_routes.route('/store_login', methods=['POST'])
def check_login():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:

        print(f"Request Headers: {request.headers}")
        print(f"Request Data: {request.data}")

        data = request.json 
        email = data['email']
        password_hash = data['password_hash']

        print(f"Received email: {email}")
        print(f"Received password_hash: {password_hash}") 

        store = s.query(Stores).filter(Stores.email == email).first()       

        if store == None:
            return { "message": "Store not found" }, 403
        
        if not store.check_password(password_hash):
            return { "message": "Wrong password" }, 403
        
        login_user(store)

        session_id = request.cookies.get('session')

        print(f"Session ID: {session_id}")

        session_id = "your_generated_session_id"  # You should generate this
        response = make_response({
            "session_id": session_id,
            "message": "Login Successful"
        }, 200)
        response.set_cookie('session', session_id, httponly=True, secure=False, samesite='Lax')  # Set secure to True in production

        return response

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return { "message": "Login Failed" }, 500
    
@store_routes.route('/stores/me', methods=['PUT'])
@login_required
def update_store():
    Session = sessionmaker(bind=engine)  # Ensure you are binding the engine here
    s = Session()
    s.begin()
    
    try:
        store = s.query(Stores).filter(Stores.id == current_user.id).first()

        if not store:
            return {"message": "Store not found"}, 404

        data = request.json  # Access the JSON data from the request

        store.store_name = data['store_name']
        store.description = data['description']
        store.image_url = data['image_url']
        store.seller_full_name = data['seller_full_name']            
        store.username = data['username']
        store.email = data['email']
        store.bank_account = data['bank_account']
        store.contact_number = data['contact_number']
        store.address = data['address']
        store.city = data['city']
        store.state = data['state']
        store.zip_code = data['zip_code']
        
        s.commit()
        return {"message": "Update user data success"}, 200

    except Exception as e:
        print(str(e))
        s.rollback()
        return {"message": "Update Failed", "error": str(e)}, 500


@store_routes.route('/store_logout', methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return { "message": "Logout Success" }

@store_routes.route('/products', methods=['POST'])
@login_required
def add_product():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        data = request.json
        new_product = Products(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            stock_quantity=data['stock_quantity'],
            image_url=data.get('image_url', ''),
            location=data.get('location', ''),
            store_id=current_user.id  # Link the product to the current logged-in store
        )
        
        s.add(new_product)
        s.commit()
        return {"message": "Product added successfully"}, 201

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to add product", "error": str(e)}, 500