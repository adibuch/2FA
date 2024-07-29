import unittest
from flask import url_for
from app import create_app
from app.models import User, db
import pyotp

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

        # יצירת משתמש לבדיקה
        self.test_user = User(username='testuser', otp_secret=pyotp.random_base32())
        self.test_user.set_password('password')
        db.session.add(self.test_user)
        db.session.commit()


    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_create_user(self):
        # בדיקה אם המשתמש נוצר ונשמר בהצלחה
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password('password'))
        print("succses")

    def test_register_get(self):
        with self.client as client:
            response = client.get('/register')
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'Redirecting...', response.data)

    def test_register_post(self):
        with self.client as client:
            response = client.post('/register', data={
                'username': 'newuser',
                'password': 'newpassword'
            })
          # בדוק שהתשובה היא הפניה מחדש
            self.assertEqual(response.status_code, 302)
        
            

    def test_login_get(self):
        with self.client as client:
            response = client.get('/login')
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'login', response.data)

    def test_login_post(self):
        with self.client as client:
            response = client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            })
            self.assertEqual(response.status_code, 302)  # צריך להפנות ל-verify_otp
            

    def test_verify_otp_get(self):
        with self.client as client:
            response = client.get('/verify_otp')
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'verify_otp', response.data)

    def test_verify_otp_post(self):
        with self.client as client:
            # ביצוע login כדי להגיע ל-verify_otp
            client.post('/login', data={
                'username': 'testuser',
                'password': 'password'
            })

            # קבלת המשתמש מהמאגר
            user = User.query.filter_by(username='testuser').first()
            totp = pyotp.TOTP(user.otp_secret)
            otp = totp.now()

            # שליחת OTP לאימות
            response = client.post('/verify_otp', data={
                'otp': otp
            })

            self.assertEqual(response.status_code, 302)  # צריך להפנות ל-dashboard
             # בדוק את כתובת ההפניה
            location = response.headers.get('Location')
           
            self.assertIsNotNone(location, "Location header should be present")
            

if __name__ == '__main__':
    unittest.main()
