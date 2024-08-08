from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
from connectors.mysql_connector import connection

from sqlalchemy.orm import sessionmaker

from controllers.stores import store_routes
from controllers.users import user_routes
import os

from flask_login import LoginManager
from models.stores import Stores

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

CORS(app, supports_credentials=True, origins=['http://localhost:3000'])

app.register_blueprint(store_routes)
app.register_blueprint(user_routes)


login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(connection)
    s = Session()
    return s.query(Stores).get(int(user_id))

@app.route("/")
def hello_world():
    return "Hello World"