from flask import Blueprint, make_response, request
from connectors.mysql_connector import connection, engine
from models.stores import Stores

from sqlalchemy.orm import sessionmaker

from flask_login import login_user, login_required, logout_user, current_user

store_routes = Blueprint("store_routes", __name__)

@store_routes.route('/store_register', methods=['POST'])
def register_seller():
    Session = sessionmaker(connection)
    s = Session()
    s.begin()

    try:
                
        NewSeller = Stores(
            seller_full_name=request.form['seller_full_name'],            
            username=request.form['username'],
            email=request.form['email'],
            store_name=request.form['store_name'],
            description=request.form['description'],
            bank_account=request.form['bank_account'],
            contact_number=request.form['contact_number'],
            image_url=request.form['image_url'],
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            zip_code=request.form['zip_code']
        )
        
        NewSeller.set_password(request.form['password_hash'])

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
    Session = sessionmaker(connection)
    s = Session()
    s.begin()
    
    try:
        store = s.query(Stores).filter(Stores.id == current_user.id).first()

        if not store:
            return {"message": "Store not found"}, 404

        store.store_name=request.form['store_name'],
        store.description=request.form['description'],
        store.image_url=request.form['image_url'],
        store.seller_full_name=request.form['seller_full_name'],            
        store.username=request.form['username'],
        store.email=request.form['email'],
        store.bank_account=request.form['bank_account'],
        store.contact_number=request.form['contact_number'],
        store.address=request.form['address'],
        store.city=request.form['city'],
        store.state=request.form['state'],
        store.zip_code=request.form['zip_code']
        
        s.commit()
        return {"message": "Update user data success"}, 200

    except Exception as e:
        print(str(e))
        s.rollback()
        return { "message": "Update Failed", 'error': str(e)}, 500

@store_routes.route('/store_logout', methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return { "message": "Logout Success" }