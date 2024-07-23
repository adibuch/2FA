
from app.models import User

# אתחול Flask app
from app import app

with app.app_context():
    # שאילתת כל המשתמשים מהטבלה User
    users = User.query.all()

    # הצגת כל המשתמשים
    for user in users:
        print(f'Username: {user.username}, OTP Secret: {user.otp_secret}')
