from . import *
def auth_routes(app:Flask ):
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

