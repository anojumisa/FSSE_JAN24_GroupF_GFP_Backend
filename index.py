from flask import Flask, jsonify, make_response, request
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
from models.products import Products

from google.cloud import storage

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config.from_object('config.Config')

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

@app.route('/featured-products', methods=['GET'])
def get_featured_products():
    limit = request.args.get('limit', default=10, type=int)
    Session = sessionmaker(connection)
    s = Session()

    # Query the database for featured products
    featured_products = s.query(Products).filter_by(featured=True).limit(limit).all()

    # Check if there are any featured products
    if not featured_products:
        return make_response(jsonify({"message": "No featured products found"}), 404)

    # Convert the products to a JSON response
    featured_products = [product.to_dict() for product in featured_products]
    response = jsonify(featured_products)
    return response

storage_client = storage.Client.from_service_account_json(app.config['GCS_CREDENTIALS'])
bucket = storage_client.get_bucket(app.config['GCS_BUCKET_NAME'])

@app.route('/upload', methods=['POST'])
def upload_image():
    file = request.files.get('image')

    if file and file.filename:
        try:
            # Validate file type (example: only allow images)
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                return jsonify({"error": "Invalid file type"}), 400

            public_url = f"https://storage.googleapis.com/{app.config['GCS_BUCKET_NAME']}/{file.filename}"
            blob = bucket.blob(file.filename)
            blob.upload_from_file(file)

            print(f"File uploaded to {public_url}")

            return make_response(jsonify({"url": public_url}), 200)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return jsonify({"error": "No file uploaded"}), 400

@app.route('/store_image_url', methods=['POST'])
def store_image_url():
    data = request.json
    print("Received data:", data)
    id = data.get('id')
    image_url = data.get('image_url')

    if id and image_url:
        Session = sessionmaker(bind=connection)
        s = Session()
        try:
            product = s.query(Products).filter_by(id=id).first()
            if product:
                product.image_url = image_url
                s.commit()
                return jsonify({"message": "Image URL updated successfully"}), 200
            else:
                return jsonify({"message": "Product not found"}), 404
        except Exception as e:
            s.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            s.close()
    else:
        return jsonify({"message": "Product ID and image URL are required"}), 400

@app.route('/user_image', methods=['POST'])
def store_image():
    data = request.json
    print("Received data:", data)
    id = data.get('id')
    image_url = data.get('image_url')

    if id and image_url:
        Session = sessionmaker(bind=connection)
        s = Session()
        try:
            user = s.query(User).filter_by(id=id).first()
            if user:
                user.image_url = image_url
                s.commit()
                return jsonify({"message": "Image updated successfully"}), 200
            else:
                return jsonify({"message": "User not found"}), 404
        except Exception as e:
            s.rollback()
            return jsonify({"error": str(e)}), 500
        finally:
            s.close()
    else:
        return jsonify({"message": "User ID and image are required"}), 400
    
if __name__ == "__main__":
    app.run(port=5000, debug=True)