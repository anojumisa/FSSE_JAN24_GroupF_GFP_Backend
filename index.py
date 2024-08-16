from flask import Flask, jsonify, make_response
from dotenv import load_dotenv
from flask_cors import CORS
from connectors.mysql_connector import connection

from sqlalchemy.orm import sessionmaker

from controllers.stores import store_routes
from controllers.users import user_routes
from controllers.category import category_routes
from controllers.product_category import product_routes
from controllers.cart import cart_routes
from controllers.order import order_routes

import os

from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from models.stores import Stores
from models.users import User

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

jwt = JWTManager(app)

CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

app.register_blueprint(store_routes)
app.register_blueprint(user_routes)
app.register_blueprint(category_routes)
app.register_blueprint(product_routes)
app.register_blueprint(cart_routes)
app.register_blueprint(order_routes)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_routes.check_login'

@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(connection)
    s = Session()
    return s.query(Stores).get(int(user_id))

@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(connection)
    s = Session()
    return s.query(User).get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return make_response(jsonify({"message": "Unauthorized access"}), 401)

@app.route("/")
def hello_world():
    return "Hello World"

if __name__ == "__main__":
    app.run(port=5000, debug=True)