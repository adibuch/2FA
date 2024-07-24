import os
import tempfile
import pyotp
import qrcode
from flask import Flask, request, render_template, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_talisman import Talisman
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecret'
db.init_app(app)
Talisman(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print(f"Attempting to register user with username: '{username}'")
        
        # בדוק אם שם המשתמש כבר קיים
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User with username '{username}' already exists.")  # הודעת דיאגנוסטיקה
            return render_template('register.html', error="שם משתמש זה כבר בשימוש")

        otp_secret = pyotp.random_base32()
        user = User(username=username, otp_secret=otp_secret)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # יצירת QR Code
        totp = pyotp.TOTP(user.otp_secret)
        otp_url = totp.provisioning_uri(user.username, issuer_name="2FA-Demo-App")
        qr = qrcode.make(otp_url)

        # שמירת ה-QR Code בקובץ זמני
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr.save(temp_file.name)

        return render_template('register_done.html', qr_code=temp_file.name)
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            return redirect(url_for('verify_otp'))
    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp = request.form['otp']
        username = session.get('username')
        user = User.query.filter_by(username=username).first()
        totp = pyotp.TOTP(user.otp_secret)
        if totp.verify(otp):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid OTP'
    return render_template('verify_otp.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/qr_code/<path:filename>')
def qr_code(filename):
    return send_file(filename, mimetype='image/png')



@app.route('/users')
def users():
    users = User.query.all()
    return {'users': [{'id': user.id, 'username': user.username, 'otp_secret': user.otp_secret} for user in users]}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
