from app import app, db
from backend.models import Admin
from werkzeug.security import generate_password_hash


with app.app_context():
    username = 'admin'
    password = 'admin@123'
    
    
    hashed_password = generate_password_hash(password)
    
    
    new_user = Admin(username=username, password=hashed_password)
    
    
    db.session.add(new_user)
    db.session.commit()

    print("Admin user created successfully!")
