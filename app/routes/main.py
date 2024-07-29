from flask import Blueprint, render_template, redirect, url_for, send_file
from flask_login import login_required, current_user
from app.models import User, db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    Redirect to the home page.

    Returns:
        str: Redirect to the home page URL.
    """
    return redirect(url_for('main.home'))

@main_bp.route('/home')
def home():
    """
    Display the home page.

    Returns:
        str: Rendered home page HTML.
    """
    return render_template('home.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Display the dashboard page.

    This page requires the user to be logged in.

    Returns:
        str: Rendered dashboard page HTML.
    """
    return render_template('dashboard.html')

@main_bp.route('/qr_code/<path:filename>')
def qr_code(filename):
    """
    Serve a QR code image file.

    Args:
        filename (str): The path to the QR code image file.

    Returns:
        Response: The QR code image file with the correct MIME type.
    """
    return send_file(filename, mimetype='image/png')

@main_bp.route('/users')
def users():
    """
    Retrieve a list of all users in the system.

    Returns:
        dict: A dictionary containing a list of users with their ID, username, and OTP secret.
    """
    users = User.query.all()
    return {'users': [{'id': user.id, 'username': user.username, 'otp_secret': user.otp_secret} for user in users]}
