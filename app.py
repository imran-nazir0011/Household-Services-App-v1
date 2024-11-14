from flask import Flask, render_template, redirect, url_for, request, session, flash
from models import db, Admin, Customer, ServiceProfessional, Service, ServiceRequest
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from config import Config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SECRET_KEY'] = Config.SECRET_KEY

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
        if role == 'Customer':
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
        # Retrieve form data
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])  # Encrypt the password
        role = request.form['role']  # Capture the selected role

        # Check if email or username already exists in the database
        existing_email = db.session.query(Customer).filter_by(email=email).first() or \
                         db.session.query(ServiceProfessional).filter_by(email=email).first() 
        existing_username = db.session.query(Customer).filter_by(username=username).first() or \
                            db.session.query(ServiceProfessional).filter_by(username=username).first() 
        
        if existing_email:
            flash('Email already exists. Please use a different email.', 'danger')
            return redirect(url_for('register'))
        elif existing_username:
            flash('Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('register'))

        # Create user based on role
        if role == 'Customer':
            new_user = Customer(name=name, username=username, email=email, password=password)
        elif role == 'ServiceProfessional':
            new_user = ServiceProfessional(name=name, username=username, email=email, password=password)
        else:
            flash('Invalid role selected', 'danger')
            return redirect(url_for('register'))
        
        # Add user to the database
        db.session.add(new_user)
        db.session.commit()

        # Redirect to login with a success message
        flash('Registration successful! You may now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('auth/register.html')

# Admin login route
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query the Admin table to find a matching username
        admin = Admin.query.filter_by(username=username).first()
        
        # Check if the admin exists and the password is correct
        if admin and check_password_hash(admin.password, password):
            # Successful login
            session['user_id'] = username
            session['role'] = 'Admin'  
            flash('Login successful', 'success')
            return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard or home page
        else:
            # Invalid credentials
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('admin_login'))
    
    return render_template('admin/login.html')
# Admin Dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    # Check if the user is an admin
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin
    
    # Get all customers and service professionals for admin view
    customers = Customer.query.all()
    service_professionals = ServiceProfessional.query.all()
    
    return render_template('admin/dashboard.html', customers=customers, service_professionals=service_professionals)

# Manage Customers (Admin can view all customers)
@app.route('/admin/customers')
def manage_customers():
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    # Fetch all customers
    customers = Customer.query.all()
    return render_template('admin/manage_customers.html', customers=customers)

# View Customer Details
@app.route('/admin/customer/<int:customer_id>', methods=['GET'])
def view_customer(customer_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('login'))  # Redirect to login if not an admin

    # Fetch customer by ID
    customer = Customer.query.get_or_404(customer_id)
    return render_template('admin/view_customer.html', customer=customer)

# Delete Customer
@app.route('/admin/delete_customer/<int:customer_id>', methods=['POST'])
def delete_customer(customer_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('login'))  # Redirect to login if not an admin

    # Fetch customer by ID
    customer = Customer.query.get_or_404(customer_id)

    # Delete the customer from the database
    db.session.delete(customer)
    db.session.commit()

    # Flash a success message
    flash('Customer has been deleted successfully!', 'success')

    # Redirect back to the customers management page
    return redirect(url_for('manage_customers'))



# View and Approve/Reject Service Professional Verification Requests
@app.route('/admin/service_professionals')
def manage_service_professionals():
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    # Fetch all service professionals
    service_professionals = ServiceProfessional.query.all()
    return render_template('admin/manage_service_professionals.html', service_professionals=service_professionals)

# Admin verifies a Service Professional's profile
@app.route('/admin/service_professionals/<int:professional_id>/verify', methods=['POST'])
def verify_service_professional(professional_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    service_professional = ServiceProfessional.query.get_or_404(professional_id)
    
    # If the service professional has requested verification
    if service_professional.verification_requested:
        service_professional.verified = True  # Mark as verified
        service_professional.verification_requested = False  # Remove verification request
        db.session.commit()
        flash(f"Service professional {service_professional.name} has been verified.", "success")
    else:
        flash(f"Service professional {service_professional.name} has not requested verification.", "danger")
    
    return redirect(url_for('manage_service_professionals'))

# Admin view all Service Requests (Pending, Assigned, and Completed)
@app.route('/admin/service_requests')
def manage_service_requests():
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    # Fetch all service requests
    service_requests = ServiceRequest.query.all()
    return render_template('admin/manage_service_requests.html', service_requests=service_requests)

# Admin view details of a Service Request
@app.route('/admin/service_requests/<int:request_id>')
def view_service_request(request_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    service_request = ServiceRequest.query.get_or_404(request_id)
    return render_template('admin/view_service_request.html', request=service_request)

# Admin can change the status of a Service Request
@app.route('/admin/service_requests/<int:request_id>/update_status', methods=['POST'])
def update_service_request_status(request_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    service_request = ServiceRequest.query.get_or_404(request_id)

    # Update the status based on the form input
    new_status = request.form['status']
    service_request.service_status = new_status
    db.session.commit()

    flash(f"Service request status updated to {new_status}.", "success")
    return redirect(url_for('view_service_request', request_id=request_id))

# Admin can delete a service request (if necessary)
@app.route('/admin/service_requests/<int:request_id>/delete', methods=['POST'])
def delete_service_request(request_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    service_request = ServiceRequest.query.get_or_404(request_id)

    db.session.delete(service_request)
    db.session.commit()

    flash("Service request deleted.", "success")
    return redirect(url_for('manage_service_requests'))

# Admin can manage Services (Add/Edit/Delete Services)
@app.route('/admin/services')
def manage_services():
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    services = Service.query.all()
    return render_template('admin/manage_services.html', services=services)

# Admin can add a new Service
@app.route('/admin/services/add', methods=['GET', 'POST'])
def add_service():
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    if request.method == 'POST':
        service_name = request.form['name']
        price = request.form['price']
        description = request.form['description']
        time_required = request.form['time_required']

        # Create new service
        new_service = Service(
            name=service_name,
            price=price,
            description=description,
            time_required=time_required
        )
        
        db.session.add(new_service)
        db.session.commit()
        
        flash(f"Service {new_service.name} added successfully.", "success")
        return redirect(url_for('manage_services'))
    
    return render_template('admin/add_service.html')

# Admin can edit an existing service
@app.route('/admin/services/<int:service_id>/edit', methods=['GET', 'POST'])
def edit_service(service_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    service = Service.query.get_or_404(service_id)

    if request.method == 'POST':
        service.name = request.form['name']
        service.price = request.form['price']
        service.description = request.form['description']
        service.time_required = request.form['time_required']

        db.session.commit()
        flash(f"Service {service.name} updated successfully.", "success")
        return redirect(url_for('manage_services'))

    return render_template('admin/edit_service.html', service=service)

# Admin can delete a service
@app.route('/admin/services/<int:service_id>/delete', methods=['POST'])
def delete_service(service_id):
    if session.get('role') != 'Admin':
        return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

    service = Service.query.get_or_404(service_id)

    db.session.delete(service)
    db.session.commit()

    flash(f"Service {service.name} deleted successfully.", "success")
    return redirect(url_for('manage_services'))

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

        # If the professional clicks to apply for verification
        if 'apply_verification' in request.form and not professional.verified:
            professional.verification_requested = True  # Set to True to indicate they have requested verification
            db.session.commit()
            flash("Your verification request has been sent to the admin for review.", "success")

        db.session.commit()
        flash("Profile updated successfully!", "success")

    return render_template('professional/profile.html', professional=professional)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)