from . import *
def  customer_routes(app:Flask ):
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
                    date_of_request=datetime.strptime(date_of_request, '%Y-%m-%d').date(),
                    service_status='pending'  # Set the default status
                )

                db.session.add(new_request)
                db.session.commit()

                flash("Your service request has been created successfully!", "success")
                return redirect(url_for('customer_dashboard'))  # Redirect to customer dashboard after creation

            # Fetch available services for the customer to choose from
            services = Service.query.all()
            return render_template('customer/create_service_request.html', services=services)

        @app.route('/customer/summary')
        def customer_summary():
            return render_template('summary.html')
