from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, Response
import io
import csv

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
def list_users():
    """
    Render the user management view.
    """
    admin_service = current_app.container.admin_service()
    users = admin_service.get_all_users()
    return render_template('admin_users.html', users=users, active_tab='users')

@admin_bp.route('/users/add', methods=['GET'])
def add_user_view():
    """
    Render the add user view.
    """
    return render_template('admin_add_user.html', active_tab='add_user')

@admin_bp.route('/settings', methods=['GET'])
def settings():
    """
    Render the system settings view.
    """
    admin_service = current_app.container.admin_service()
    config = admin_service.get_academic_year_config()
    return render_template('admin_settings.html', config=config, active_tab='settings')

@admin_bp.route('/import', methods=['GET'])
def import_data():
    """
    Render the data import view.
    """
    return render_template('admin_import.html', active_tab='import')

@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Redirect legacy dashboard route to users list.
    """
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/create', methods=['POST'])
def create_user():
    """
    Create a new user.
    """
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    
    if not all([username, password, role]):
        flash('Username, password, and role are required', 'danger')
        return redirect(url_for('admin.list_users'))
        
    try:
        admin_service = current_app.container.admin_service()
        admin_service.create_user(username, password, role, first_name, last_name)
        flash(f'User {username} created successfully', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error creating user: {str(e)}', 'danger')
        
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/delete', methods=['POST'])
def delete_user():
    """
    Delete a user.
    """
    user_id = request.form.get('user_id')
    
    if not user_id:
        flash('User ID is required', 'danger')
        return redirect(url_for('admin.list_users'))
        
    try:
        admin_service = current_app.container.admin_service()
        admin_service.hard_delete_user(user_id)
        flash('User deleted successfully', 'success')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'danger')
        
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/delete-bulk', methods=['POST'])
def bulk_delete_users():
    """
    Delete multiple users.
    """
    user_ids = request.form.getlist('user_ids')
    
    if not user_ids:
        flash('No users selected', 'warning')
        return redirect(url_for('admin.list_users'))
        
    try:
        admin_service = current_app.container.admin_service()
        result = admin_service.bulk_delete_users(user_ids)
        
        if result['errors'] > 0:
            flash(f"Deleted {result['success']} users. Failed to delete {result['errors']} users.", 'warning')
        else:
            flash(f"Successfully deleted {result['success']} users.", 'success')
            
    except Exception as e:
        flash(f'Error performing bulk delete: {str(e)}', 'danger')
        
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/settings/update', methods=['POST'])
def update_settings():
    """
    Update system settings (academic year).
    """
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    if not all([start_date, end_date]):
        flash('Start and end dates are required', 'danger')
        return redirect(url_for('admin.settings'))
        
    try:
        admin_service = current_app.container.admin_service()
        admin_service.set_academic_year(start_date, end_date)
        flash('Academic year settings updated', 'success')
    except ValueError as e:
        flash(str(e), 'danger')
    except Exception as e:
        flash(f'Error updating settings: {str(e)}', 'danger')
        
    return redirect(url_for('admin.settings'))

@admin_bp.route('/import/users', methods=['POST'])
def import_users():
    """
    Handle user import via CSV.
    """
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin.import_data'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin.import_data'))
        
    if file:
        try:
            # Convert to text stream for the service
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            import_service = current_app.container.import_service()
            result = import_service.process_user_csv(stream)
            
            if result['errors'] > 0:
                flash(f"Import completed with errors. Success: {result['success']}, Errors: {result['errors']}", 'warning')
            else:
                flash(f"Import successful. Added {result['success']} users.", 'success')
                
        except Exception as e:
            flash(f"Error processing file: {str(e)}", 'danger')
            
    return redirect(url_for('admin.import_data'))

@admin_bp.route('/import/grades', methods=['POST'])
def import_grades():
    """Handle grade import via CSV."""
    return _handle_import('process_grade_csv', 'grades')

@admin_bp.route('/import/attendance', methods=['POST'])
def import_attendance():
    """Handle attendance import via CSV."""
    return _handle_import('process_attendance_csv', 'attendance')

@admin_bp.route('/import/surveys', methods=['POST'])
def import_surveys():
    """Handle survey import via CSV."""
    return _handle_import('process_survey_csv', 'surveys')

def _handle_import(method_name, type_label):
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('admin.import_data'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('admin.import_data'))
        
    if file:
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            import_service = current_app.container.import_service()
            method = getattr(import_service, method_name)
            result = method(stream)
            
            if result['errors'] > 0:
                flash(f"Import completed with errors. Success: {result['success']}, Errors: {result['errors']}", 'warning')
            else:
                flash(f"Import successful. Added {result['success']} {type_label}.", 'success')
        except Exception as e:
            flash(f"Error processing file: {str(e)}", 'danger')
            
    return redirect(url_for('admin.import_data'))

@admin_bp.route('/import/template/<type>', methods=['GET'])
def download_template(type):
    """Download CSV template for imports."""
    si = io.StringIO()
    cw = csv.writer(si)
    
    if type == 'users':
        cw.writerow(['username', 'password_hash', 'role', 'student_id', 'name', 'email'])
        cw.writerow(['jdoe', 'hashed_pw', 'student', 'S12345', 'John Doe', 'john@example.com'])
    elif type == 'grades':
        cw.writerow(['student_id', 'module_code', 'grade'])
        cw.writerow(['S12345', 'WM9QF', '85'])
    elif type == 'attendance':
        cw.writerow(['student_id', 'module_code', 'date', 'status'])
        cw.writerow(['S12345', 'WM9QF', '2025-10-01', 'Present'])
    elif type == 'surveys':
        cw.writerow(['student_id', 'week', 'stress', 'sleep'])
        cw.writerow(['S12345', '5', '3', '7.5'])
    else:
        return "Invalid template type", 400
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=template_{type}.csv"}
    )
