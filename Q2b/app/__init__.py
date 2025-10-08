from flask import Flask
from flask_mongoengine import MongoEngine, Document
from flask_login import LoginManager

def create_app():
    app = Flask(__name__)
    app.config['MONGODB_SETTINGS'] = {
        'db': 'library',
        'host': 'localhost',
        'port': 27017
    }

    app.static_folder = 'assets'
    db = MongoEngine(app)

    app.config['SECRET_KEY'] = 'isaaclim009'

    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    # We will configure the rest of login_manager in a later step

    return app, db, login_manager

app, db, login_manager = create_app()

# We will add the user_loader and other imports here in later steps