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

    @app.route('/professional/summary')
    def professional_summary():
        return render_template('summary.html')