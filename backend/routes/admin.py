from . import *

def admin_routes(app:Flask ):

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


    @app.route('/admin/customers', methods=['GET', 'POST'])
    def manage_customers():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin login if not an admin

        if request.method == 'POST':
            # Get the action from the form
            action = request.form.get('action')
            customer_id = request.form.get('customer_id')

            # Fetch the customer by ID
            customer = Customer.query.get_or_404(customer_id)

            if action == 'verify':
                # Verify the customer
                customer.verification_status = True
                flash(f'Customer {customer.name} has been verified!', 'success')

            elif action== 'reject':

                customer.verification_status = False
                flash(f'Customer {customer.name} has been rejected!', 'danger')

            elif action == 'delete':
                # Anonymize the customer data
                temp = customer.name
                customer.name = "Deleted Customer"
                customer.username = f"deleted_{customer.id}"
                customer.password = generate_password_hash("deleted")
                customer.email = None
                customer.phone = None
                customer.address = None
                customer.verification_status = False

                # Cancel all pending service requests of the customer
                if customer.service_requests:
                    for req in customer.service_requests:
                        if req.service_status not in ['completed','canceled']:  # Check if the service request is pending
                            req.service_status = 'canceled'  # Update the status to canceled
                            req.remarks = "Service request canceled as the customer is no longer active."
                
                flash(f'Customer {temp} has been anonymized, and their pending service requests have been canceled!', 'warning')

               

            # Commit the changes
            db.session.commit()

            # Redirect back to the manage customers page
            return redirect(url_for('manage_customers'))

        # For GET requests, fetch all customers
        customers = Customer.query.all()
        return render_template('admin/manage_customers.html', customers=customers)


    @app.route('/admin/service_professionals', methods=['GET', 'POST'])
    def manage_service_professionals():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin login if not an admin

        # Handle action requests (approve, reject, delete)
        if request.method == 'POST':
            # Get the service professional ID and the action from the form
            professional_id = request.form.get('professional_id')
            action = request.form.get('action')

            # Fetch the service professional by ID
            service_professional = ServiceProfessional.query.get_or_404(professional_id)

            if action == "approve":
                # Approve the service professional
                service_professional.verified = True
                flash(f"Service professional {service_professional.name} has been approved.", "success")
            elif action == "reject":
                # Reject the service professional
                service_professional.verified = False
                flash(f"Service professional {service_professional.name} has been rejected.", "danger")
            elif action == 'delete':
                    # Anonymize the service professional data
                    temp = service_professional.name
                    service_professional.name = "Deleted Professional"
                    service_professional.username = f"deleted_{service_professional.id}"
                    service_professional.password = generate_password_hash("deleted")
                    service_professional.email = None
                    service_professional.phone = None
                    service_professional.service_type = None
                    service_professional.verified = False

                    # Cancel all pending or ongoing service requests of the service professional
                    if service_professional.service_requests:
                        for req in service_professional.service_requests:
                            if req.service_status not in ['completed','canceled']:  # Check if the service request is not completed
                                req.service_status = 'canceled'  # Update the status to canceled
                                req.remarks = "Service request canceled as the assigned service professional is no longer active."


                    flash(f'Service professional {temp} has been anonymized, and their associated service requests have been canceled!', 'warning')

            else:
                flash("Invalid action specified.", "warning")

            # Commit the changes to the database
            db.session.commit()

            # Redirect back to the manage service professionals page
            return redirect(url_for('manage_service_professionals'))

        # For GET requests, fetch all service professionals
        service_professionals = ServiceProfessional.query.all()
        return render_template(
            'admin/manage_service_professionals.html',
            service_professionals=service_professionals
        )

    @app.route('/admin/service_requests', methods=['GET', 'POST'])
    def manage_service_requests():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin_login if not an admin

        # Fetch all service requests
        service_requests = ServiceRequest.query.all()

        if request.method == 'POST':
            # Handle actions (approve, reject, delete, update status)
            request_id = request.form.get('request_id')
            action = request.form.get('action')

            service_request = ServiceRequest.query.get_or_404(request_id)

            if action == 'update_status':
                # Handle status update
                new_status = request.form.get('status')
                if new_status:
                    service_request.service_status = new_status
                    db.session.commit()
                    flash(f"Service request #{request_id} status updated to '{new_status}'.", "success")
                else:
                    flash("No status provided for the update.", "danger")

            elif action == 'cancel':
                # Handle cancel request
                if service_request.service_status not in ['completed', 'canceled']:
                    service_request.service_status = 'canceled'
                    db.session.commit()
                    flash(f"Service request #{request_id} has been canceled.", "success")
                else:
                    flash(f"Service request #{request_id} cannot be canceled.", "danger")

            return redirect(url_for('manage_service_requests'))

        # Render the admin page with all service requests
        return render_template('admin/manage_service_requests.html', service_requests=service_requests)



    @app.route('/admin/services', methods=['GET', 'POST'])
    def manage_services():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin login if not an admin

        # Handle viewing services (GET request without action)
        if request.method == 'GET' and 'action' not in request.args:
            services = Service.query.all()  # Fetch all services
            return render_template('admin/manage_services.html', services=services)

        # Handle the action part (Redirect to add or edit)
        if request.method == 'POST':
            action = request.form.get('action')  # Get the action from the form

            if action == 'add':
                return redirect(url_for('add_service'))  # Redirect to the 'add_service' route

            elif action == 'edit':
                service_id = request.form['service_id']
                return redirect(url_for('edit_service', service_id=service_id))  # Redirect to the 'edit_service' route

            elif action == 'DELETE':
                    service_id = request.form.get('service_id')
                    service = Service.query.get_or_404(service_id)

                    # Anonymize the service details
                    service.name = "Deleted Service"
                    service.price = 0.0
                    service.description = "This service has been deleted."
                    service.time_required = 0
                    service.image = None

                    # Commit the changes
                    db.session.commit()

                    flash(f"Service '{service.name}' has been anonymized and marked as deleted.", "warning")
                    return redirect(url_for('manage_services'))

        return redirect(url_for('manage_services'))  # If no valid action, redirect to the manage services page

    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'images')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(filename: str) -> bool:
        ext = filename.rsplit('.', 1)[-1].lower()  
        return ext in ALLOWED_EXTENSIONS

    @app.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
    def edit_service(service_id):
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin login if not an admin

        service = Service.query.get_or_404(service_id)

        if request.method == 'POST':
            # Handle the form submission for editing the service
            service.name = request.form['name']
            service.price = request.form['price']
            service.description = request.form['description']
            service.time_required = request.form['time_required']

            # Handle image upload (optional)
            if 'image' in request.files:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    image_filename = secure_filename(f"{service.name}.{image.filename.rsplit('.', 1)[1].lower()}")
                    image.save(os.path.join(UPLOAD_FOLDER, image_filename))
                    service.image = image_filename

            db.session.commit()
            flash(f"Service '{service.name}' updated successfully.", "success")
            return redirect(url_for('manage_services'))  # Redirect back to manage services after update

        return render_template('admin/add_edit_service.html', service=service, action='edit')  # For GET request, show the edit form

    @app.route('/admin/services/add', methods=['GET', 'POST'])
    def add_service():
        if session.get('role') != 'Admin':
            return redirect(url_for('admin_login'))  # Redirect to admin login if not an admin

        if request.method == 'POST':
            # Handle the form submission for adding the service
            service_name = request.form['name']
            price = request.form['price']
            description = request.form['description']
            time_required = request.form['time_required']

            # Handle image upload (optional)
            image_filename = None
            if 'image' in request.files:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    image_filename = secure_filename(f"{service_name}.{image.filename.rsplit('.', 1)[1].lower()}")
                    image.save(os.path.join(UPLOAD_FOLDER, image_filename))

            # Add the new service
            new_service = Service(
                name=service_name,
                price=price,
                description=description,
                time_required=time_required,
                image=image_filename
            )
            db.session.add(new_service)
            db.session.commit()
            flash(f"Service '{new_service.name}' added successfully.", "success")
            return redirect(url_for('manage_services'))  # Redirect back to manage services after adding

        return render_template('admin/add_edit_service.html', action='add')  # For GET request, show the add form


    @app.route('/admin/summary')
    def admin_summary():
        return render_template('summary.html')

