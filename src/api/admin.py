from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
import io

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/import', methods=['GET', 'POST'])
def import_users():
    """
    Handle user import via CSV.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return render_template('admin.html'), 400
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return render_template('admin.html'), 400
            
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
                
    return render_template('admin.html')

@admin_bp.route('/import/academic', methods=['GET', 'POST'])
def import_academic():
    """
    Handle academic data import via CSV.
    """
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return render_template('admin.html'), 400
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return render_template('admin.html'), 400
            
        if file:
            try:
                # Convert to text stream for the service
                stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
                import_service = current_app.container.import_service()
                result = import_service.process_academic_csv(stream)
                
                if result['errors'] > 0:
                    flash(f"Import completed with errors. Success: {result['success']}, Errors: {result['errors']}", 'warning')
                else:
                    flash(f"Import successful. Added {result['success']} records.", 'success')
                    
            except Exception as e:
                flash(f"Error processing file: {str(e)}", 'danger')

    return render_template('admin.html')
