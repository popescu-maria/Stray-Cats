# app/__init__.py

import os
from flask import Flask
# from app.config import Config
from app.extensions import db, login_manager, init_extensions
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    load_dotenv()

    # Configure your app
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_default_secret_key_if_not_set')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_extensions(app)

    from .controllers.app import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        db.create_all() # Create database tables based on models

    return app