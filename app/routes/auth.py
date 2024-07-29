from flask import Blueprint, render_template, request, redirect, url_for, session
from flask_login import login_user, logout_user, login_required
from app.models import db, User
import pyotp
import qrcode
import tempfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Register a new user in the system.

    On a GET request, it displays the registration form.
    On a POST request, it registers the new user if the username does not already exist in the system.

    Returns:
        str: HTML page.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Username exists in the system")

        otp_secret = pyotp.random_base32()
        user = User(username=username, otp_secret=otp_secret)
        user.set_password(password)
        db.session.add(user)  # Using the correct db instance
        db.session.commit()

        totp = pyotp.TOTP(user.otp_secret)
        otp_url = totp.provisioning_uri(user.username, issuer_name="2FA-Demo-App")
        qr = qrcode.make(otp_url)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr.save(temp_file.name)

        return render_template('register_done.html', qr_code=temp_file.name)
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Log in an existing user.

    On a GET request, it displays the login form.
    On a POST request, it verifies the user's credentials and initiates the OTP verification process.

    Returns:
        str: HTML page or a redirect to the OTP verification page.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('auth.verify_otp'))
        else:
            return render_template('login.html', error="wrong password")
    return render_template('login.html')

@auth_bp.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    """
    Verify the OTP for the logged-in user.

    On a GET request, it displays the OTP verification form.
    On a POST request, it verifies the provided OTP and logs in the user if the OTP is correct.

    Returns:
        str: HTML page or a redirect to the dashboard.
    """
    if request.method == 'POST':
        otp = request.form['otp']
        print(f"Received OTP: {otp}")
        username = session.get('username')
        
        user = User.query.filter_by(username=username).first()
        print(f"Found user: {user.username}")
        totp = pyotp.TOTP(user.otp_secret)
        print(totp.verify(otp))
        if totp.verify(otp):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            return 'Invalid OTP'
    return render_template('verify_otp.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """
    Log out the current user.

    Returns:
        str: Redirect to the login page.
    """
    logout_user()
    return redirect(url_for('auth.login'))
