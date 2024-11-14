from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Admin model remains unchanged as it has no direct relationships
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(15))
    address = db.Column(db.String(255))

    # Relationship to access service requests directly from a customer
    service_requests = db.relationship('ServiceRequest', back_populates='customer', lazy=True)

class ServiceProfessional(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(15))
    service_type = db.Column(db.String(50))  # Specifies the type of service they provide, e.g., "plumber"
    experience = db.Column(db.Integer)       # Experience in years
    verified = db.Column(db.Boolean, default=False)

    # Relationship to access service requests assigned to the professional
    service_requests = db.relationship('ServiceRequest', back_populates='professional', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # e.g., "Plumbing", "AC Repair"
    price = db.Column(db.Float, nullable=False)      # Base price for this service
    description = db.Column(db.Text)
    time_required = db.Column(db.Integer)            # Time in minutes

    # Relationship to access service requests for this service
    service_requests = db.relationship('ServiceRequest', back_populates='service', lazy=True)

class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('service_professional.id'))
    date_of_request = db.Column(db.DateTime)
    date_of_completion = db.Column(db.DateTime)
    service_status = db.Column(db.String(20))
    remarks = db.Column(db.Text)

    # Establish relationships with foreign key references
    service = db.relationship('Service', back_populates='service_requests')
    customer = db.relationship('Customer', back_populates='service_requests')
    professional = db.relationship('ServiceProfessional', back_populates='service_requests')

