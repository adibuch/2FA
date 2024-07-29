from app import create_app
from app.models import db

app = create_app()

with app.app_context():
    # מחיקת כל הטבלאות
    db.drop_all()
    # יצירת כל הטבלאות מחדש
    db.create_all()
    print("Database has been reset.")
