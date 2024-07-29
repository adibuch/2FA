import unittest
from flask import url_for
from app import create_app
from app.models import User, db
import pyotp

class MainTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['TESTING'] = True
        self.app.config['SERVER_NAME'] = 'localhost'
        self.app.config['APPLICATION_ROOT'] = '/'
        self.app.config['PREFERRED_URL_SCHEME'] = 'http'
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # יצירת משתמש עם OTP לצורך הבדיקות
        self.test_user = User(username='testuser', otp_secret=pyotp.random_base32())
        self.test_user.set_password('testpassword')
        db.session.add(self.test_user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_index_redirect(self):
        with self.client:
            response = self.client.get(url_for('main.index'))
            self.assertEqual(response.status_code, 302)  # צפוי redirect
            #self.assertEqual(response.location, url_for('main.home', _external=True))

    def test_home_page(self):
        with self.client:
            response = self.client.get(url_for('main.home'))
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'home', response.data)

    def test_dashboard_access(self):
        with self.client:
            # התחברות עם משתמש קיים
            self.client.post(url_for('auth.login'), data={
                'username': 'testuser',
                'password': 'testpassword'
            })

            # הנחה שה-OTP נבדק כראוי
            otp = pyotp.TOTP(self.test_user.otp_secret).now()
            self.client.get(url_for('auth.verify_otp'), query_string={'otp': otp})

            # גישה לדף ה-dashboard
            response = self.client.get(url_for('main.dashboard'))
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'dashboard', response.data)

    def test_qr_code(self):
        with self.client:
            # התחברות עם משתמש קיים
            self.client.post(url_for('auth.login'), data={
                'username': 'testuser',
                'password': 'testpassword'
            })

            # הנחה שה-OTP נבדק כראוי
            otp = pyotp.TOTP(self.test_user.otp_secret).now()
            self.client.get(url_for('auth.verify_otp'), query_string={'otp': otp})

            # גישה לקובץ QR Code
            response = self.client.get(url_for('main.qr_code', filename='test_qr.png'))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.mimetype, 'text/html')

if __name__ == '__main__':
    unittest.main()
