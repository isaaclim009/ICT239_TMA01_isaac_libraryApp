from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager

# This function creates and configures the Flask app
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

    # We will initialize the LoginManager in a later step
    login_manager = LoginManager()
    login_manager.init_app(app)

    return app, db, login_manager

app, db, login_manager = create_app()

# We will add the user loader and other imports here later