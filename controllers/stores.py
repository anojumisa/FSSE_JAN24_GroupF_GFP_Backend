from flask import Blueprint, jsonify, make_response, request
from connectors.mysql_connector import connection, engine
from models.stores import Stores
from models.products import Products

from sqlalchemy.orm import sessionmaker
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

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
        NewSeller.set_password(password_hash)
        
        s.add(NewSeller)
        s.commit()

    except Exception as e:
        print(e)
        s.rollback()
        return { "message": "Register Failed" }, 500
    
    return { "message": "Register Success" }, 200

@store_routes.route('/store_login', methods=['POST'])
def check_login_jwt():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        data = request.json 
        email = data['email']

        store = s.query(Stores).filter(Stores.email == email).first()                

        if store is None:
            return { "message": "User not found" }, 403
        
        if not store.check_password(data['password_hash']):
            return { "message": "Invalid password" }, 403

        access_token = create_access_token(identity=store.id, additional_claims={"name": store.store_name, "id": store.id})
        return {
            "access_token": access_token,
            "message": "Login Success"
        }, 200        

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return { "message": "Login Failed" }, 500

@store_routes.route('/stores/me', methods=['PUT'])
@jwt_required()
def update_store():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()
    
    try:
        store_id = get_jwt_identity()
        store = s.query(Stores).filter(Stores.id == store_id).first()

        if not store:
            return {"message": "Store not found"}, 404

        data = request.json

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

@store_routes.route('/store_logout', methods=['POST'])
@jwt_required()
def user_logout():
    return { "message": "Logout Success" }

@store_routes.route('/products', methods=['POST'])
@jwt_required()
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
            store_id=get_jwt_identity()
        )
        
        s.add(new_product)
        s.commit()
        return {"message": "Product added successfully"}, 201

    except Exception as e:
        s.rollback()
        print(f"Exception: {e}")
        return {"message": "Failed to add product", "error": str(e)}, 500

@store_routes.route('/products', methods=['GET'])
def get_products():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        products = s.query(Products).all()      

        products_list = [{
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "stock": p.stock_quantity,
        "store_id": p.store_id
        } for p in products]

        return {
            'products': products_list,
        }, 200

    except Exception as e:
        print(e)
        return { 'message': 'Unexpected Error' }, 500

@store_routes.route('/product/<id>', methods=['GET'])
def get_product(id):
  Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:

        query = s.query(Products).filter(Products.id == id).first()

        product = {
        "name": query.name,
        "description": query.description,
        "price": query.price,
        "stock_quantity": query.stock_quantity,
        "image_url": query.image_url,        
        "store_id": query.store_id
        }

        return {
            'product': product,
        }, 200

    except Exception as e:
        print(e)
        return { 'message': 'Unexpected Error' }, 500
      
# @store_routes.route('/products', methods=['GET'])
# @jwt_required()
# def get_products():
#     Session = sessionmaker(bind=engine)
#     s = Session()
#     s.begin()

#     try:
#         store = get_jwt_identity()
#         products = s.query(Products).filter(Products.store_id == store).all()        
#         products_list = [{"id": p.id, "name": p.name, "price": p.price} for p in products]

#         return {
#             'products': products_list,
#         }, 200

#     except Exception as e:
#         print(e)
#         return { 'message': 'Unexpected Error' }, 500
    
@store_routes.route('/store/products_overview', methods=['GET'])
@jwt_required()
def get_products_overview():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        store_id = get_jwt_identity()
        products = s.query(Products).filter(Products.store_id == store_id).all()

        products_list = [{
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "stock_quantity": p.stock_quantity
        } for p in products]

        return jsonify({
            "products": products_list,
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to fetch product overview"}), 500

@store_routes.route('/store/info', methods=['GET'])
@jwt_required()
def get_store_info():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        store_id = get_jwt_identity()
        store = s.query(Stores).filter(Stores.id == store_id).first()

        if store is None:
            return jsonify({"message": "Store not found"}), 404

        store_info = {
            "store_name": store.store_name,
            "description": store.description,
            "bank_account": store.bank_account,
            "contact_number": store.contact_number,
            "address": store.address,
            "city": store.city,
            "state": store.state,
            "zip_code": store.zip_code,
            "image_url": store.image_url
        }

        return jsonify(store_info), 200

    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to fetch store info"}), 500

@store_routes.route('/store/orders', methods=['GET'])
@jwt_required()
def get_orders():
    Session = sessionmaker(bind=engine)
    s = Session()
    s.begin()

    try:
        store_id = get_jwt_identity()
        orders = s.query(Orders).filter(Orders.store_id == store_id).all()

        orders_list = [{
            "order_id": o.id,
            "total_amount": o.total,
            "delivery_date": o.delivery_date 
        } for o in orders]

        return jsonify({
            "orders": orders_list
        }), 200

    except Exception as e:
        print(e)
        return jsonify({"message": "Failed to fetch orders"}), 500
