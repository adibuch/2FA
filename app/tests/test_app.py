import pytest
from app import app, db
from models import User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    # נתונים לרישום משתמש חדש
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }
    # שליחת בקשה לרישום משתמש חדש
    response = client.post('/register', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"qr_code" in response.data

    # בדיקת שמירת המשתמש בבסיס הנתונים
    with app.app_context():
        user = User.query.filter_by(username='testuser').first()
        assert user is not None
        assert user.check_password('testpassword')
