from app import app, db
from backend.models import Admin
from werkzeug.security import generate_password_hash

# Set up the app context to interact with the database
with app.app_context():
    username = 'admin'
    password = 'admin@123'
    
    # Generate hashed password
    hashed_password = generate_password_hash(password)
    
    # Create new admin user
    new_user = Admin(username=username, password=hashed_password)
    
    # Add the new user to the session and commit to the database
    db.session.add(new_user)
    db.session.commit()

    print("Admin user created successfully!")
