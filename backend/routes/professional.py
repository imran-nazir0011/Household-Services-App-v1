from . import *
def professional_routes(app:Flask ):
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

    @app.route('/professional/pending_requests', methods=['GET', 'POST'])
    def view_pending_requests():
        # Fetch the logged-in professional's ID from the session
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))  # Redirect to login if not logged in

        # Get the ServiceProfessional object for the logged-in user
        professional = ServiceProfessional.query.get(user_id)
        if not professional or not professional.verified:
            flash("You are not verified as a professional or you don't exist!", "danger")
            return render_template('professional/pending_requests.html')  # Stay on the current page with a flash message

        if request.method == 'POST':
            # Action to accept the request
            request_id = request.form.get('request_id')
            service_request = ServiceRequest.query.get(request_id)
            if service_request:
                # Update the service request status to 'assigned' and assign the professional
                service_request.service_status = 'assigned'
                service_request.professional_id = user_id  # Assign the logged-in professional to the request
                db.session.commit()
                flash("Service request accepted.", "success")
            else:
                flash("Request not found.", "danger")

            return redirect(url_for('view_pending_requests'))  # After action, reload the page

        # Fetch the service type of the professional
        service_type = professional.service_type

        # Fetch pending service requests that match the professional's service type
        pending_requests = ServiceRequest.query.filter_by(
            professional_id=None,  # Only requests that are not assigned yet
            service_status='pending',  # Only pending requests
            service_id=Service.query.filter_by(name=service_type).first().id  # Filter by service type
        ).all()

        return render_template('professional/pending_requests.html', requests=pending_requests)



    # View Accepted Requests for the Service Professional
    @app.route('/professional/accepted_requests')
    def view_accepted_requests():
        # Fetch the logged-in professional's ID from the session
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))  # Redirect to login if not logged in

        # Fetch the accepted service requests assigned to this professional
        accepted_requests = (ServiceRequest.query.filter(
                                        ServiceRequest.professional_id == user_id,
                                        ServiceRequest.service_status != 'pending'
                                        ).all())
        return render_template('professional/accepted_requests.html', requests=accepted_requests)

    @app.route('/professional/requests/<int:request_id>/complete')
    def professional_complete_request(request_id):
        # Fetch the service request by ID
        service_request = ServiceRequest.query.get(request_id)
        if service_request:
            # Update the service request status to 'completed'
            service_request.service_status = 'completed'
            service_request.date_of_completion = datetime.utcnow()  # Record the time of completion
            service_request.remarks = 'Service has been completed by the professional.'
            db.session.commit()
            flash("Service request marked as completed.", "success")
        else:
            flash("Request not found.", "danger")
        
        return redirect(url_for('view_accepted_requests'))


    # Professional Profile Management
    @app.route('/professional/profile', methods=['GET', 'POST'])
    def professional_profile():
        professional = ServiceProfessional.query.get(session['user_id'])
        services = Service.query.all()  # Fetch all services

        if request.method == 'POST':
            # Update profile details
            professional.name = request.form['name']
            professional.email = request.form['email']
            professional.phone = request.form['phone']
            professional.experience = request.form['experience']

            # Allow service type update only if it's currently "None"
            if professional.service_type == "None" or not professional.service_type:
                professional.service_type = request.form['service_type']

            db.session.commit()
            flash("Profile updated successfully!", "success")

        return render_template('professional/profile.html', professional=professional, services=services)


    @app.route('/professional/summary')
    def professional_summary():
        return render_template('summary.html')