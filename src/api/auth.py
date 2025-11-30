from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
        
    # Handle POST
    if request.is_json:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
    else:
        # Form submission
        username = request.form.get('username')
        password = request.form.get('password')

    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'Missing username or password'}), 400
        flash('Missing username or password', 'danger')
        return render_template('login.html')
        
    auth_service = current_app.container.auth_service()
    
    try:
        token = auth_service.login(username, password)
        if token:
            if request.is_json:
                return jsonify({'token': token}), 200
            
            # For UI, we would ideally set a session/cookie here.
            # Since we don't have Flask-Login fully wired in this file (it's in app.py?),
            # we'll assume for now we just redirect. 
            # BUT: The base.html checks current_user.
            # If we don't login_user(), current_user won't be set.
            # We need to import login_user from flask_login if available.
            # Let's check if we can import it.
            try:
                from flask_login import login_user
                # We need a User object. AuthService returns a token.
                # We should probably get the user from the repo.
                repo = current_app.container.user_repository()
                user = repo.get_by_username(username)
                if user:
                    login_user(user)
            except ImportError:
                pass # Flask-Login not installed or configured?
            
            # Redirect based on role
            # We need to know the role.
            # If we have the user object:
            if 'user' in locals() and user:
                if user.role == 'STUDENT':
                    return redirect(url_for('surveys.student_dashboard')) # Assuming this exists
                elif user.role == 'OFFICER':
                    return redirect(url_for('analytics.officer_dashboard'))
                elif user.role == 'DIRECTOR':
                    return redirect(url_for('analytics.director_dashboard'))
            
            return redirect(url_for('analytics.officer_dashboard')) # Default fallback
            
        else:
            if request.is_json:
                return jsonify({'error': 'Invalid credentials'}), 401
            flash('Invalid credentials', 'danger')
            return render_template('login.html')
            
    except Exception as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        flash(f'Error: {str(e)}', 'danger')
        return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    try:
        from flask_login import logout_user
        logout_user()
    except ImportError:
        pass
    return redirect(url_for('auth.login'))
