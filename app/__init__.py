from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_talisman import Talisman
from config import Config
from dotenv import load_dotenv
from app.models import db
import os

load_dotenv()  # טען את הקובץ .env
#db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    Talisman(app)
    
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # רישום הפונקציה ליצירת הדאטאבייס
    with app.app_context():
        db.create_all()
    
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))
