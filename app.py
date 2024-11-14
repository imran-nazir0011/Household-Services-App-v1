from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, Admin, Customer, ServiceProfessional, Service, ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///household_services.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

# index route
@app.route('/')
def index():
    return render_template('base.html')

@app.route('/logout')
def logout():
    # Clear the session to log the user out
    session.pop('user_id', None)
    session.pop('role', None)  # Also clear the role from the session
    return redirect(url_for('index'))  # Redirect to the home page after logout

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Retrieve login form data
        role = request.form.get('role')  # 'Admin', 'Customer', 'ServiceProfessional'
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = None
        
        # Check role and query the corresponding user model
        if role == 'Admin':
            user = Admin.query.filter_by(username=username).first()
        elif role == 'Customer':
            user = Customer.query.filter_by(username=username).first()
        elif role == 'ServiceProfessional':
            user = ServiceProfessional.query.filter_by(username=username).first()

        # If user exists and password is correct, log them in
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = role  # Store role in session to manage access
            
            # Redirect to respective dashboard based on role
            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'Customer':
                return redirect(url_for('customer_dashboard'))
            elif role == 'ServiceProfessional':
                return redirect(url_for('professional_dashboard'))
        else:
            flash("Invalid credentials or role", "danger")
            return redirect(url_for('login'))

    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Retrieve form data, including the role
        name=request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])  # Encrypt the password
        role = request.form['role']  # Capture the selected role
        
        # Check role and create an instance of the appropriate model
        if role == 'Customer':
            new_user = Customer(name=name, username=username, email=email, password=password)
        elif role == 'ServiceProfessional':
            new_user = ServiceProfessional(name=name, username=username, email=email, password=password)
        elif role == 'Admin':
            new_user = Admin(username=username, password=password)
        else:
            flash('Invalid role selected', 'danger')
            return redirect(url_for('register'))
        
        # Add user to the database
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))  # Redirect to the login page after registration

    return render_template('auth/register.html')

# Admin Routes
@app.route('/admin/dashboard')
def admin_dashboard():
    # Fetch data needed for admin view (e.g., all services, users, etc.)
    return render_template('admin/dashboard.html')

@app.route('/admin/services')
def admin_manage_services():
    services = Service.query.all()
    return render_template('admin/manage_services.html', services=services)

@app.route('/admin/services/create', methods=['GET', 'POST'])
def admin_create_service():
    if request.method == 'POST':
        # Create a new service based on form input
        new_service = Service(
            name=request.form['name'],
            price=request.form['price'],
            time_required=request.form['time_required'],
            description=request.form['description']
        )
        db.session.add(new_service)
        db.session.commit()
        return redirect(url_for('admin_manage_services'))
    return render_template('admin/create_service.html')

# Customer Routes
@app.route('/customer/dashboard')
def customer_dashboard():
    # Retrieve the logged-in user's ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in
    # Query the Customer model based on the user ID in the session
    customer = Customer.query.get(user_id)

    return render_template('customer/dashboard.html', customer=customer)

@app.route('/customer/request_service', methods=['GET', 'POST'])
def customer_request_service():
    if request.method == 'POST':
        # Create a new service request for the customer
        new_request = ServiceRequest(
            service_id=request.form['service_id'],
            customer_id=session['user_id'],  # Assuming user_id stored in session
            date_of_request=request.form['date_of_request']
        )
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('customer_dashboard'))
    return render_template('customer/request_service.html')

# View Available Services for the Customer
@app.route('/customer/services')
def view_services():
    services = Service.query.all()  # Fetch all available services from the database
    return render_template('customer/view_services.html', services=services)

# View Customer's Service Requests
@app.route('/customer/service_requests')
def view_service_requests():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch service requests for this customer
    service_requests = ServiceRequest.query.filter_by(customer_id=user_id).all()
    return render_template('customer/view_service_requests.html', requests=service_requests)

# Create a New Service Request
@app.route('/customer/create_service_request', methods=['GET', 'POST'])
def create_service_request():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        # Get the selected service and request date
        service_id = request.form['service_id']
        date_of_request = request.form['date_of_request']

        # Check if the user selected a service
        if not service_id:
            flash("Please select a service.", "danger")
            return redirect(url_for('create_service_request'))

        # Create a new service request
        new_request = ServiceRequest(
            service_id=service_id,
            customer_id=user_id,
            date_of_request=date_of_request,
            service_status='pending'  # Set the default status
        )

        db.session.add(new_request)
        db.session.commit()

        flash("Your service request has been created successfully!", "success")
        return redirect(url_for('customer_dashboard'))  # Redirect to customer dashboard after creation

    # Fetch available services for the customer to choose from
    services = Service.query.all()
    return render_template('customer/create_service_request.html', services=services)


# Service Professional Routes
@app.route('/professional/dashboard')
def professional_dashboard():
    # Fetch the logged-in service professional's data
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch the service professional's details
    professional = ServiceProfessional.query.get(user_id)
    if not professional:
        return redirect(url_for('login'))  # Redirect if the professional is not found

    return render_template('professional/dashboard.html', professional=professional)

# View Pending Requests for the Service Professional
@app.route('/professional/pending_requests')
def view_pending_requests():
    # Fetch the logged-in professional's ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch pending service requests assigned to this professional
    pending_requests = ServiceRequest.query.filter_by(professional_id=None, service_status='pending').all()

    return render_template('professional/pending_requests.html', requests=pending_requests)

@app.route('/professional/requests/<int:request_id>/accept')
def professional_accept_request(request_id):
    # Fetch the service request by ID
    service_request = ServiceRequest.query.get(request_id)
    if service_request:
        # Update the service request status to 'assigned' and assign the professional
        service_request.service_status = 'assigned'
        service_request.professional_id = session['user_id']  # Assign the logged-in professional to the request
        db.session.commit()
        flash("Service request accepted.", "success")
    else:
        flash("Request not found.", "danger")
    
    return redirect(url_for('view_pending_requests'))

# View Accepted Requests for the Service Professional
@app.route('/professional/accepted_requests')
def view_accepted_requests():
    # Fetch the logged-in professional's ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch the accepted service requests assigned to this professional
    accepted_requests = ServiceRequest.query.filter_by(professional_id=user_id, service_status='assigned').all()

    return render_template('professional/accepted_requests.html', requests=accepted_requests)

@app.route('/professional/requests/<int:request_id>/complete')
def professional_complete_request(request_id):
    # Fetch the service request by ID
    service_request = ServiceRequest.query.get(request_id)
    if service_request:
        # Update the service request status to 'completed'
        service_request.service_status = 'completed'
        service_request.date_of_completion = datetime.utcnow()  # Record the time of completion
        db.session.commit()
        flash("Service request marked as completed.", "success")
    else:
        flash("Request not found.", "danger")
    
    return redirect(url_for('view_accepted_requests'))


# Professional Profile Management
@app.route('/professional/profile', methods=['GET', 'POST'])
def professional_profile():
    professional = ServiceProfessional.query.get(session['user_id'])

    if request.method == 'POST':
        # Get updated profile details from the form
        professional.name = request.form['name']
        professional.email = request.form['email']
        professional.phone = request.form['phone']
        professional.service_type = request.form['service_type']
        professional.experience = request.form['experience']

        db.session.commit()
        flash("Profile updated successfully!", "success")

    return render_template('professional/profile.html', professional=professional)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
