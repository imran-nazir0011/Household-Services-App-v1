from . import *
def professional_routes(app:Flask ):
     
    @app.route('/professional/dashboard')
    def professional_dashboard():
         
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))   

         
        professional = ServiceProfessional.query.get(user_id)
        if not professional:
            return redirect(url_for('login'))   

        return render_template('professional/dashboard.html', professional=professional)

    @app.route('/professional/pending_requests', methods=['GET', 'POST'])
    def view_pending_requests():
         
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))   

         
        professional = ServiceProfessional.query.get(user_id)
        if not professional or not professional.verified:
            flash("You are not verified as a professional or you don't exist!", "danger")
            return render_template('professional/pending_requests.html')   

        if request.method == 'POST':
             
            request_id = request.form.get('request_id')
            service_request = ServiceRequest.query.get(request_id)
            if service_request:
                 
                service_request.service_status = 'assigned'
                service_request.professional_id = user_id   
                service_request.remarks=f'Service request assigned to {professional.name}.'
                db.session.commit()
                flash("Service request accepted.", "success")
            else:
                flash("Request not found.", "danger")

            return redirect(url_for('view_pending_requests'))   

         
        service_type = professional.service_type

         
        pending_requests = ServiceRequest.query.filter_by(
            professional_id=None,   
            service_status='pending',   
            service_id=Service.query.filter_by(name=service_type).first().id   
        ).all()

        return render_template('professional/pending_requests.html', requests=pending_requests)



     
    @app.route('/professional/accepted_requests')
    def view_accepted_requests():
         
        user_id = session.get('user_id')
        if not user_id:
            return redirect(url_for('login'))   

         
        accepted_requests = (ServiceRequest.query.filter(
                                        ServiceRequest.professional_id == user_id,
                                        ServiceRequest.service_status != 'pending'
                                        ).all())
        return render_template('professional/accepted_requests.html', requests=accepted_requests)

    @app.route('/professional/requests/<int:request_id>/complete')
    def professional_complete_request(request_id):
         
        user_id = session.get('user_id')
        service_request = ServiceRequest.query.get(request_id)
        professional = ServiceProfessional.query.get(user_id)

        if service_request:
             
            service_request.service_status = 'completed'
            service_request.date_of_completion = datetime.utcnow()   
            service_request.remarks = f'Service has been completed by {professional.name}.'
            db.session.commit()
            flash("Service request marked as completed.", "success")
        else:
            flash("Request not found.", "danger")
        
        return redirect(url_for('view_accepted_requests'))


     
    @app.route('/professional/profile', methods=['GET', 'POST'])
    def professional_profile():
        professional = ServiceProfessional.query.get(session['user_id'])
        services = Service.query.all()   

        if request.method == 'POST':
             
            professional.name = request.form['name']
            professional.email = request.form['email']
            professional.phone = request.form['phone']
            professional.experience = request.form['experience']
            professional.address = request.form['address']

             
            if professional.service_type == "None" or not professional.service_type:
                professional.service_type = request.form['service_type']

            db.session.commit()
            flash("Profile updated successfully!", "success")

        return render_template('professional/profile.html', professional=professional, services=services)


