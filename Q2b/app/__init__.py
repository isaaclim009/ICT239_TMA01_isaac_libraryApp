from flask import Flask
from flask_mongoengine import MongoEngine, Document
from flask_login import LoginManager
from app.models.users import User

def create_app():
    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = { 'db': 'library', 'host': 'localhost', 'port': 27017 }
    app.static_folder = 'assets'
    db = MongoEngine(app)
    app.config['SECRET_KEY'] = 'isaaclim009'

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please login or register first\nto get an account'
    login_manager.login_message_category = 'info'

    return app, db, login_manager

app, db, login_manager = create_app()

@login_manager.user_loader
def load_user(user_id):
    return User.getUserById(user_id)