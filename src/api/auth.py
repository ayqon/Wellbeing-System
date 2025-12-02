from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login via form or JSON.
    """
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
            
            # Attempt to log in user via Flask-Login if available
            user = None
            try:
                from flask_login import login_user
                repo = current_app.container.user_repository()
                user = repo.get_by_username(username)
                if user:
                    login_user(user)
            except ImportError:
                pass  # pragma: no cover 
            
            # Redirect based on role
            if user:
                if user.role == 'STUDENT':
                    return redirect(url_for('surveys.student_dashboard'))
                elif user.role == 'OFFICER':
                    return redirect(url_for('analytics.officer_dashboard'))
                elif user.role == 'DIRECTOR':
                    return redirect(url_for('analytics.director_dashboard'))
            
            return redirect(url_for('analytics.officer_dashboard'))
            
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
    """
    Handle user logout.
    """
    try:
        from flask_login import logout_user
        logout_user()
    except ImportError:  # pragma: no cover
        pass
    return redirect(url_for('auth.login'))
