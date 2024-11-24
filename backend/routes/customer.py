from . import *
def  customer_routes(app:Flask ):
         
        @app.route('/customer/dashboard')
        def customer_dashboard():
             
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('login'))   
             
            customer = Customer.query.get(user_id)

            return render_template('customer/dashboard.html', customer=customer)

        @app.route('/customer/request_service', methods=['GET', 'POST'])
        def customer_request_service():
            if request.method == 'POST':
                 
                new_request = ServiceRequest(
                    service_id=request.form['service_id'],
                    customer_id=session['user_id'],   
                    date_of_request=request.form['date_of_request']
                )
                db.session.add(new_request)
                db.session.commit()
                return redirect(url_for('customer_dashboard'))
            return render_template('customer/request_service.html')

         
        @app.route('/customer/services')
        def view_services():
            services = Service.query.all()   
            return render_template('customer/view_services.html', services=services)

         
        @app.route('/customer/service_requests')
        def view_service_requests():
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('login'))   

             
            service_requests = ServiceRequest.query.filter_by(customer_id=user_id).all()
            return render_template('customer/view_service_requests.html', requests=service_requests)
        
        @app.route('/customer/cancel_service_request/<int:request_id>', methods=['POST'])
        def cancel_service_request(request_id):
             
            user_id = session.get('user_id')
            if not user_id:
                flash("You must be logged in to cancel a service request.", "danger")
                return redirect(url_for('login'))

             
            service_request = ServiceRequest.query.filter_by(id=request_id, customer_id=user_id).first()
            if not service_request:
                flash("Service request not found or you do not have permission to cancel it.", "danger")
                return redirect(url_for('view_service_requests'))

             
            if service_request.service_status != 'pending':
                flash("Only pending service requests can be canceled.", "warning")
                return redirect(url_for('view_service_requests'))

             
            service_request.service_status = 'canceled'
            service_request.remarks = 'Service request has been canceled by the customer.'

            db.session.commit()

            flash("The service request has been successfully canceled.", "success")
            return redirect(url_for('view_service_requests'))

         
        @app.route('/customer/create_service_request', methods=['GET', 'POST'])
        def create_service_request():
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('login'))   

            if request.method == 'POST':
                 
                service_id = request.form['service_id']
                date_of_request = request.form['date_of_request']

                 
                if not service_id:
                    flash("Please select a service.", "danger")
                    return redirect(url_for('create_service_request'))

                 
                new_request = ServiceRequest(
                    service_id=service_id,
                    customer_id=user_id,
                    date_of_request=datetime.strptime(date_of_request, '%Y-%m-%d').date(),
                    service_status='pending',
                    remarks='Service request is pending, awaiting professional assignment'
                )

                db.session.add(new_request)
                db.session.commit()

                flash("Your service request has been created successfully!", "success")
                return redirect(url_for('customer_dashboard'))   

             
            services = Service.query.all()
            return render_template('customer/create_service_request.html', services=services)

        @ app.route('/customer/profile', methods=['GET', 'POST'])
        def customer_profile():
            user_id = session.get('user_id')
            if not user_id:
                return redirect(url_for('login'))   

            customer = Customer.query.get(user_id)
            if request.method == 'POST':
                 
                customer.email = request.form['email']
                customer.phone = request.form['phone']
                customer.address = request.form['address']
                db.session.commit()
                flash("Profile updated successfully!", "success")
                return redirect(url_for('customer_profile'))

            return render_template('customer/profile.html', customer=customer)
