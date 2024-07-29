import unittest
from app import create_app, db
from app.models import User
import pyotp

class UserModelTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_set_password(self):
        u = User(username='test')
        u.set_password('test_password')
        self.assertTrue(u.check_password('test_password'))
        self.assertFalse(u.check_password('wrong_password'))

    def test_create_user(self):
        u = User(username='test_user', otp_secret=pyotp.random_base32())
        u.set_password('password')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(User.query.filter_by(username='test_user').first())

if __name__ == '__main__':
    unittest.main()
