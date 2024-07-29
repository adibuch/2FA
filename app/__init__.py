from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_talisman import Talisman
from config import Config
from dotenv import load_dotenv
from app.models import db
import os

# Load environment variables from a .env file
load_dotenv()

# Initialize the LoginManager
login_manager = LoginManager()

def create_app():
    """
    Factory function to create and configure the Flask application.
    
    This function initializes the Flask app with the following:
    - Configuration settings from the Config object
    - Database initialization
    - Talisman for security headers
    - LoginManager for user session management
    
    It also registers the authentication and main blueprints.
    
    Returns:
        app (Flask): The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize the database with the app
    db.init_app(app)
    
    # Initialize Talisman for security headers
    Talisman(app)
    
    # Initialize the LoginManager with the app
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Create database tables if they do not exist
    with app.app_context():
        db.create_all()
    
    # Register the authentication blueprint
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Register the main blueprint
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    """
    Load a user by their ID.

    This function is used by Flask-Login to manage user sessions.
    
    Args:
        user_id (int): The ID of the user to be loaded.
        
    Returns:
        User: The user object corresponding to the given user ID.
    """
    from app.models import User
    return User.query.get(int(user_id))
