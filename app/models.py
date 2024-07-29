from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize SQLAlchemy for database interactions
db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    User model for storing user information and handling authentication.

    Attributes:
        id (int): The primary key for the user.
        username (str): The username of the user, unique and not nullable.
        password_hash (str): The hashed password of the user.
        otp_secret (str): The secret key for OTP (One-Time Password) generation.

    Methods:
        set_password(password):
            Hashes the provided password and stores it in the password_hash attribute.
        
        check_password(password):
            Checks if the provided password matches the stored hashed password.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    otp_secret = db.Column(db.String(16), nullable=False)
    
    def set_password(self, password):
        """
        Hash the provided password and store it in the password_hash attribute.
        
        Args:
            password (str): The password to be hashed and stored.
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Check if the provided password matches the stored hashed password.
        
        Args:
            password (str): The password to be checked against the stored hash.
        
        Returns:
            bool: True if the password matches the hash, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

