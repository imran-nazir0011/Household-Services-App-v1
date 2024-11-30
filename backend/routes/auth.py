from . import *
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
def auth_routes(app:Flask ):
         
        @app.route('/')
        def index():
            return render_template('home.html')

        @app.route('/logout')
        def logout():
             
            session.pop('user_id', None)
            session.pop('role', None)   
            return redirect(url_for('index'))   

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                 
                role = request.form.get('role')   
                username = request.form.get('username')
                password = request.form.get('password')
                
                user = None
                
                 
                if role == 'Customer':
                    user = Customer.query.filter_by(username=username).first()
                elif role == 'ServiceProfessional':
                    user = ServiceProfessional.query.filter_by(username=username).first()

                 
                if user and check_password_hash(user.password, password):
                    session['user_id'] = user.id
                    session['role'] = role   
                    
                     
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
                 
                name = request.form['name']
                username = request.form['username']
                email = request.form['email']
                password = generate_password_hash(request.form['password'])   
                role = request.form['role']   

                 
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

                 
                if role == 'Customer':
                    new_user = Customer(name=name, username=username, email=email, password=password)
                elif role == 'ServiceProfessional':
                    new_user = ServiceProfessional(name=name, username=username, email=email, password=password)
                else:
                    flash('Invalid role selected', 'danger')
                    return redirect(url_for('register'))
                
                 
                db.session.add(new_user)
                db.session.commit()

                 
                flash('Registration successful! You may now log in.', 'success')
                return redirect(url_for('login'))

            return render_template('auth/register.html')
        
        @app.route('/search', methods=['GET'])
        def search():
            if 'query' not in request.args or 'type' not in request.args:
                flash("Please enter a search query.", "warning")
                if session.get('role') == 'Admin':
                    return redirect(url_for('admin_dashboard'))
                elif session.get('role') == 'Customer':
                    return redirect(url_for('customer_dashboard'))
                elif session.get('role') == 'ServiceProfessional':
                    return redirect(url_for('professional_dashboard'))
                else:
                    return redirect(url_for('index'))

            query = request.args['query']
            search_type = request.args['type']

            results = []

            if session.get('role') == 'Admin':
                if search_type == 'customers':
                    results = Customer.query.filter( or_(Customer.name.contains(query),Customer.address.contains(query))).all()
                    return render_template('admin/manage_customers.html', customers=results)
                elif search_type == 'professionals':
                    results = ServiceProfessional.query.filter(or_(ServiceProfessional.name.contains(query),ServiceProfessional.address.contains(query))).all()
                    return render_template('admin/manage_service_professionals.html', service_professionals=results)
                elif search_type == 'requests':
                     
                    results = ServiceRequest.query.join(Customer).join(Service).join(ServiceProfessional).filter(or_(ServiceRequest.service_status.contains(query),Customer.address.contains(query),ServiceProfessional.name.contains(query),Service.name.contains(query))).all()
                    return render_template('admin/manage_service_requests.html', service_requests=results)
                elif search_type == 'services':
                    results = Service.query.filter(Service.name.contains(query)|Service.price.contains(query)).all()
                    return render_template('admin/manage_services.html', services=results)
                else:
                    flash("Invalid search type.", "danger")
                    return redirect(url_for('admin_dashboard'))

            elif session.get('role') == 'Customer':
                if search_type == 'services':
                    results = Service.query.filter(Service.name.contains(query)).all()
                    return render_template('customer/view_services.html', services=results)
                elif search_type == 'requests':
                     
                    results = (ServiceRequest.query.join(Service).filter(and_(ServiceRequest.customer_id == session.get('user_id'),Service.name.contains(query))).all())
                    return render_template('customer/view_service_requests.html', requests=results)

                else:
                    flash("Invalid search type.", "danger")
                    return redirect(url_for('customer_dashboard'))
                
            elif session.get('role') == 'ServiceProfessional':
                if search_type == 'pending':
                     
                    professional = ServiceProfessional.query.get(session['user_id'])
                                         
                    results = (
                        ServiceRequest.query
                        .join(Customer)
                        .join(Service)
                        .filter(
                            and_(
                                ServiceRequest.service_status == 'pending',
                                Service.name == professional.service_type,   
                                or_(
                                    Customer.address.contains(query),
                                    Customer.name.contains(query)
                                )
                            )
                        )
                        .all()
                    )
                    return render_template('professional/pending_requests.html', requests=results)

                
                elif search_type == 'requests':
                    results = (
                                    ServiceRequest.query

                                    .join(Customer)
                                    .filter(
                                        
                                            and_(
                                                ServiceRequest.professional_id == session.get('user_id'),
                                                ServiceRequest.service_status != 'pending',
                                                or_(
                                                    Customer.name.contains(query),
                                                    Customer.address.contains(query)
                                                     )
                                                 )   
                                             ).all() )
                    return render_template('professional/accepted_requests.html', requests=results)

                else:
                    flash("Invalid search type.", "danger")
                    return redirect(url_for('professional_dashboard'))

            else:
                flash("Invalid role or access denied.", "danger")
                return redirect(url_for('index'))

        

        def generate_admin_plots(summary_data):
            plot_files = []
            plot_folder = 'static/plots'
            os.makedirs(plot_folder, exist_ok=True)

            # Customers and Professionals Distribution Pie Chart
            admin_plot = 'user_professional_distribution.png'
            if os.path.exists(os.path.join(plot_folder, admin_plot)):
                os.remove(os.path.join(plot_folder, admin_plot))   
            labels = ['Customers', 'Professionals']
            sizes = [summary_data['total_customers'], summary_data['total_professionals']]
            plt.figure(figsize=(6, 6))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.title('Customers and Professionals Distribution')
            plt.savefig(os.path.join(plot_folder, admin_plot))
            plt.close()
            plot_files.append(admin_plot)

            # Customer Verification Status Bar Chart
            customer_verification_plot = 'customer_verification_status.png'
            if os.path.exists(os.path.join(plot_folder, customer_verification_plot)):
                os.remove(os.path.join(plot_folder, customer_verification_plot))   
            labels = ['Verified', 'Not Verified', 'Deleted Customers']
            customer_counts = [
                summary_data['verified_customers'],
                summary_data['unverified_customers'],
                summary_data['deleted_customers']
            ]
            plt.figure(figsize=(8, 5))
            plt.bar(labels, customer_counts, color=['green', 'red', 'blue'])
            plt.title('Verified vs Not Verified Customers vs Deleted Customers')
            plt.ylabel('Number of Customers')
            plt.savefig(os.path.join(plot_folder, customer_verification_plot))
            plt.close()
            plot_files.append(customer_verification_plot)

            # Professional Verification Status Bar Chart
            professional_verification_plot = 'professional_verification_status.png'
            if os.path.exists(os.path.join(plot_folder, professional_verification_plot)):
                os.remove(os.path.join(plot_folder, professional_verification_plot))   
            labels = ['Verified', 'Not Verified', 'Deleted Professionals']
            professional_counts = [
                summary_data['verified_professionals'],
                summary_data['unverified_professionals'],
                summary_data['deleted_professionals']
            ]
            plt.figure(figsize=(8, 5))
            plt.bar(labels, professional_counts, color=['blue', 'orange', 'green'])
            plt.title('Verified vs Not Verified Professionals')
            plt.ylabel('Number of Professionals')
            plt.savefig(os.path.join(plot_folder, professional_verification_plot))
            plt.close()
            plot_files.append(professional_verification_plot)

            # Active vs Inactive Services Bar Chart
            service_status_plot = 'service_status_distribution.png'
            if os.path.exists(os.path.join(plot_folder, service_status_plot)):
                os.remove(os.path.join(plot_folder, service_status_plot))   
            service_labels = ['Active Services', 'Inactive Services']
            service_counts = [summary_data['active_services'], summary_data['inactive_services']]
            plt.figure(figsize=(8, 5))
            plt.bar(service_labels, service_counts, color=['purple', 'grey'])
            plt.title('Active vs Inactive Services')
            plt.ylabel('Number of Services')
            plt.savefig(os.path.join(plot_folder, service_status_plot))
            plt.close()
            plot_files.append(service_status_plot)

            # Service Request Status Distribution Bar Chart
            request_status_plot = 'service_request_status_distribution.png'
            if os.path.exists(os.path.join(plot_folder, request_status_plot)):
                os.remove(os.path.join(plot_folder, request_status_plot))   
            request_labels = ['Completed', 'Canceled', 'Pending', 'Assigned']
            request_counts = [
                summary_data['completed_requests'],
                summary_data['canceled_requests'],
                summary_data['pending_requests'],
                summary_data['assigned_requests']
            ]
            plt.figure(figsize=(10, 6))
            plt.bar(request_labels, request_counts, color=['green', 'red', 'orange', 'blue'])
            plt.title('Service Request Status Distribution')
            plt.ylabel('Number of Requests')
            plt.savefig(os.path.join(plot_folder, request_status_plot))
            plt.close()
            plot_files.append(request_status_plot)

            # Service Counts Bar Chart
            service_counts_plot = 'service_counts_distribution.png'
            if os.path.exists(os.path.join(plot_folder, service_counts_plot)):
                os.remove(os.path.join(plot_folder, service_counts_plot))   
            service_data = summary_data['requests_by_service']
            service_names = [item['service'] for item in service_data]
            service_counts = [item['count'] for item in service_data]
            plt.figure(figsize=(12, 6))
            plt.bar(service_names, service_counts, color='teal')
            plt.xticks(rotation=45, ha='right')
            plt.title('Number of Requests per Service')
            plt.ylabel('Number of Requests')
            plt.xlabel('Services')
            plt.tight_layout()  # Ensure labels fit in the plot area
            plt.savefig(os.path.join(plot_folder, service_counts_plot))
            plt.close()
            plot_files.append(service_counts_plot)

            return plot_files

         
        def generate_customer_plots(summary_data):
            plot_files = []
            plot_folder = 'static/plots'
            os.makedirs(plot_folder, exist_ok=True)

             
            customer_summary_plot = 'customer_summary.png'
            
             
            if os.path.exists(os.path.join(plot_folder, customer_summary_plot)):
                os.remove(os.path.join(plot_folder, customer_summary_plot))
            
             
            labels = ['Completed Requests', 'Pending Requests', 'Canceled Requests', 'Assigned Requests']
            values = [
                 
                summary_data['completed_requests'], 
                summary_data['pending_requests'],
                summary_data['canceled_requests'],
                summary_data['assigned_requests']
            ]
            
             
            plt.figure(figsize=(8, 6))
            plt.bar(labels, values, color=['green', 'orange', 'red', 'purple'])
            plt.title('My Service Requests')
            plt.ylabel('Number of Requests')
            plt.xticks(rotation=45, ha="right")   
            plt.tight_layout()   
            
             
            plt.savefig(os.path.join(plot_folder, customer_summary_plot))
            plt.close()
            
             
            plot_files.append(customer_summary_plot)

            return plot_files
        
        def generate_professional_plots(summary_data):
            plot_files = []
            plot_folder = 'static/plots'
            os.makedirs(plot_folder, exist_ok=True)

             
            professional_summary_plot = 'professional_summary.png'
            if os.path.exists(os.path.join(plot_folder, professional_summary_plot)):
                os.remove(os.path.join(plot_folder, professional_summary_plot))   
            labels = ['Pending Requests', 'Completed Requests', 'Assigned Requests', 'Canceled Requests']
            values = [
                summary_data['pending_requests'],
                summary_data['completed_requests'],
                summary_data['assigned_requests'],
                summary_data['canceled_requests'],
            ]
            plt.figure(figsize=(8, 5))
            plt.bar(labels, values, color=['orange', 'green', 'blue', 'red'])
            plt.title('Service Requests Overview')
            plt.ylabel('Number of Requests')
            plt.savefig(os.path.join(plot_folder, professional_summary_plot))
            plt.close()
            plot_files.append(professional_summary_plot)

            return plot_files

        @app.route('/summary', methods=['GET', 'POST'])
        def summary():
            role = session.get('role')
            summary_data = {}
            plot_files = []   

             
            if role == 'Admin':
                
                summary_data['total_customers'] = Customer.query.count()
                summary_data['total_professionals'] = ServiceProfessional.query.count()
                summary_data['total_services'] = Service.query.count()

                 
                summary_data['verified_customers'] = Customer.query.filter(Customer.verification_status == True, Customer.name != 'Deleted Customer').count()

                 
                summary_data['unverified_customers'] = Customer.query.filter(Customer.verification_status == False, Customer.name != 'Deleted Customer').count()

                 
                summary_data['deleted_customers'] = summary_data['total_customers'] - summary_data['verified_customers'] - summary_data['unverified_customers']

                 
                summary_data['verified_professionals'] = ServiceProfessional.query.filter(ServiceProfessional.verified == True, ServiceProfessional.name != 'Deleted Professional').count()

                 
                summary_data['unverified_professionals'] = ServiceProfessional.query.filter(ServiceProfessional.verified == False, ServiceProfessional.name != 'Deleted Professional').count()

                 
                summary_data['deleted_professionals'] = summary_data['total_professionals'] - summary_data['verified_professionals'] - summary_data['unverified_professionals']

                 
                summary_data['active_services'] = Service.query.filter(Service.name != "Deleted Service").count()

                 
                summary_data['inactive_services'] = Service.query.filter(Service.name == "Deleted Service").count()

                 
                summary_data['pending_requests'] = ServiceRequest.query.filter(ServiceRequest.service_status == 'pending').count()

                 
                summary_data['completed_requests'] = ServiceRequest.query.filter(ServiceRequest.service_status == 'completed').count()

                 
                summary_data['assigned_requests'] = ServiceRequest.query.filter(ServiceRequest.service_status == 'assigned').count()

                 
                summary_data['canceled_requests'] = ServiceRequest.query.filter(ServiceRequest.service_status == 'canceled').count()
                
                service_requests_count = db.session.query(
                                                    Service.name, db.func.count(ServiceRequest.id)
                                                ).join(ServiceRequest).group_by(Service.name).all()
                
                summary_data['requests_by_service'] = [
                                    {"service": service_name, "count": count} for service_name, count in service_requests_count
                                ]

                plot_files = generate_admin_plots(summary_data)

            elif role == 'Customer':
                user_id = session.get('user_id')
                summary_data['my_requests'] = ServiceRequest.query.filter_by(customer_id=user_id).count()
                summary_data['completed_requests'] = ServiceRequest.query.filter_by(
                    customer_id=user_id, service_status='completed').count()
                summary_data['pending_requests'] = ServiceRequest.query.filter_by(
                    customer_id=user_id, service_status='pending').count()
                summary_data['canceled_requests'] = ServiceRequest.query.filter_by(
                    customer_id=user_id, service_status='canceled').count()
                summary_data['assigned_requests'] = ServiceRequest.query.filter_by(
                    customer_id=user_id, service_status='assigned').count()


                 
                plot_files = generate_customer_plots(summary_data)

            elif role == 'ServiceProfessional':
                user_id = session.get('user_id')
                summary_data['pending_requests'] = ServiceRequest.query.filter_by(
                    professional_id=user_id, service_status='pending').count()
                summary_data['completed_requests'] = ServiceRequest.query.filter_by(
                    professional_id=user_id, service_status='completed').count()
                summary_data['assigned_requests'] = ServiceRequest.query.filter_by(
                    professional_id=user_id, service_status='assigned').count()
                summary_data['canceled_requests'] = ServiceRequest.query.filter_by(
                    professional_id=user_id, service_status='canceled').count()

                 
                plot_files = generate_professional_plots(summary_data)

             
            return render_template(
                'summary.html',
                role=role,
                summary_data=summary_data,
                plot_files=plot_files
            )
