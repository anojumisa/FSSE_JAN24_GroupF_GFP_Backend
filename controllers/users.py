from flask import Blueprint, request

from connectors.mysql_connector import connection
from sqlalchemy.orm import sessionmaker
from models.users import User

from flask_login import login_user, logout_user, login_required



user_routes = Blueprint("user_routes", __name__)

@user_routes.route('/register', methods=['POST'])
def register_user():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        NewUser = User(
            user_id=request.form['user_id'],
            username=request.form['username'],
            email=request.form['email'],
            password_hash=request.form['password_hash'],
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            address=request.form['address'],
            city=request.form['city'],
            state=request.form['state'],
            zip_code=request.form['zip_code'],
            image_url=request.form['image_url']
        )

        NewUser.set_password(request.form['password_hash'])

        s.add(NewUser)
        s.commit()
    except Exception as e:
        s.rollback()
        print(f"Exception:{e}")
        return { "message": "Fail to Register"}, 500
    
    return { "message": "Register Success" }, 200

@user_routes.route('/login', methods=['POST'])
def check_login():
    Session = sessionmaker(connection)
    s = Session()

    s.begin()
    try:
        email = request.form['email']
        user = s.query(User).filter(User.email == email).first()

        if user == None:
            return { "message": "User not found" }, 403
        
        if not user.check_password(request.form['password']):
            return { "message": "Invalid password" }, 403
        
        
        login_user(user)

        # Get Session ID
        session_id = request.cookies.get('session')

        return {
            "session_id": session_id,
            "message": "Login Success"
        }, 200

    except Exception as e:
        s.rollback()
        return { "message": "Login Failed" }, 500
    
@user_routes.route('/logout', methods=['GET'])
@login_required
def user_logout():
    logout_user()
    return { "message": "Logout Success" }