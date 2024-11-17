from . import *



def admin_routes(app:Flask ):
    # Define the folder where images will be saved
    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
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

    @app.route('/admin/service_professionals/<int:professional_id>/<string:action>', methods=['POST'])
    def manage_service_professional(professional_id, action):
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

        service_professional = ServiceProfessional.query.get_or_404(professional_id)

        if action == "approve":
            # Approve the service professional
            service_professional.verified = True
            service_professional.verification_requested = False  # Clear the verification request
            db.session.commit()
            flash(f"Service professional {service_professional.name} has been approved.", "success")
        elif action == "reject":
            # Reject the service professional
            service_professional.verified = False
            service_professional.verification_requested = False  # Clear the verification request
            db.session.commit()
            flash(f"Service professional {service_professional.name} has been rejected.", "danger")
        elif action == "delete":
            # Delete the service professional
            db.session.delete(service_professional)
            db.session.commit()
            flash(f"Service professional {service_professional.name} has been deleted.", "success")
        else:
            flash("Invalid action.", "warning")

        return redirect(url_for('manage_service_professionals'))

    # Admin view all Service Requests (Pending, Assigned, and Completed)
    @app.route('/admin/service_requests')
    def manage_service_requests():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

        # Fetch all service requests
        service_requests = ServiceRequest.query.all()
        return render_template('admin/manage_service_requests.html', service_requests=service_requests)
    
    @app.route('/customer/service_request_action/<int:request_id>', methods=['POST'])
    def service_request_action(request_id):
        # Fetch the service request by ID
        service_request = ServiceRequest.query.get_or_404(request_id)

        # Determine the action from the form submission
        action = request.form.get('action')

        if action == 'update_status':
            # Handle status update
            new_status = request.form.get('status')
            if new_status:
                service_request.service_status = new_status
                db.session.commit()
                flash(f"Service request #{request_id} status updated to '{new_status}'.", "success")
            else:
                flash("No status provided for the update.", "danger")

        elif action == 'delete':
            # Handle delete request
            db.session.delete(service_request)
            db.session.commit()
            flash(f"Service request #{request_id} has been deleted.", "success")

        return redirect(url_for('manage_service_requests'))



    # Admin can manage Services (Add/Edit/Delete Services)
    @app.route('/admin/services')
    def manage_services():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

        services = Service.query.all()
        return render_template('admin/manage_services.html', services=services)

    # Check if the uploaded file is an allowed image type
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.route('/admin/services/add', methods=['GET', 'POST'])
    def add_service():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

        if request.method == 'POST':
            service_name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            time_required = request.form['time_required']

            # Handle image upload
            image_filename = None
            if 'image' in request.files:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    image_filename = secure_filename(f"{service_name}.{image.filename.rsplit('.', 1)[1].lower()}")
                    image.save(os.path.join(UPLOAD_FOLDER, image_filename))

            # Create new service
            new_service = Service(
                name=service_name,
                price=price,
                description=description,
                time_required=time_required,
                image=image_filename  # Save the image filename in the database
            )
            
            db.session.add(new_service)
            db.session.commit()
            
            flash(f"Service {new_service.name} added successfully.", "success")
            return redirect(url_for('manage_services'))
        
        return render_template('admin/add_edit_service.html', service=None)



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

        return render_template('admin/add_edit_service.html', service=service)

    @app.route('/admin/services/<int:service_id>/delete', methods=['POST'])
    def delete_service(service_id):
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

        service = Service.query.get_or_404(service_id)

        db.session.delete(service)
        db.session.commit()

        flash(f"Service {service.name} deleted successfully.", "success")
        return redirect(url_for('manage_services'))

    @app.route('/admin/summary')
    def admin_summary():
        return render_template('summary.html')

