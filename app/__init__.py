import os
from flask import Flask
# from app.config import Config
from app.extensions import db
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    # app.config.from_object(Config)
    load_dotenv()

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from .controllers.app import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # You can add other blueprints or configurations here

    # This block is for initial database creation when the app starts.
    # IMPORTANT: In a production environment, use a proper migration tool like Flask-Migrate
    # to handle schema changes. Running create_all() like this will not handle migrations
    # and can lead to data loss if tables already exist and their schema changes.
    with app.app_context():
        db.create_all() # Create database tables based on models

    return app
