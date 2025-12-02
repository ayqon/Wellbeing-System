from flask import Blueprint, request, jsonify, current_app, render_template
from flask_login import login_required, current_user
from src.models.survey import WellbeingSurvey, SurveyStatus

survey_bp = Blueprint('surveys', __name__)


@survey_bp.route('/submit', methods=['POST'])
def submit_survey():
    """
    Submit a wellbeing survey response
    
    Request Body (JSON):
        student_id (str): Student's unique identifier
        week (int): Week number (1-52)
        year (int): Academic year
        stress (int): Stress level (1-5)
        sleep (int): Sleep hours (0-24)
    
    Returns:
        201: Survey submitted successfully
        400: Invalid input (missing fields, validation errors)
        404: Student not found
        409: Survey already completed (cannot resubmit)
    """
    try:
        # Parse request
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
            
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        required_fields = ['student_id', 'week', 'year', 'stress', 'sleep']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        student_id = data['student_id']
        week = data['week']
        year = data['year']
        stress = data['stress']
        sleep = data['sleep']
        
        survey_service = current_app.container.survey_service()
        
        survey = survey_service.submit_response(
            student_id=student_id,
            week=week,
            year=year,
            stress=stress,
            sleep=sleep
        )
        
        # Build response
        survey_data = {
            'survey_id': getattr(survey, 'survey_id', None),
            'student_id': getattr(survey, 'student_id', None),
            'week': getattr(survey, 'week', None),
            'year': getattr(survey, 'year', None),
            'stress': getattr(survey, 'stress', None),
            'sleep': getattr(survey, 'sleep', None),
            'is_critical': getattr(survey, 'is_critical', None)
        }
        
        try:
            status = getattr(survey, 'status', None)
            if status is not None:
                survey_data['status'] = getattr(status, 'value', None) or str(status)
            else:
                survey_data['status'] = None
        except:
            survey_data['status'] = None
        
        return jsonify({
            'message': 'Survey submitted successfully',
            'survey': survey_data
        }), 201
        
    except ValueError as e:
        error_msg = str(e)
        
        if 'not found' in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        elif 'already completed' in error_msg.lower():
            return jsonify({'error': error_msg}), 409
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@survey_bp.route('/skip', methods=['POST'])
def skip_survey():
    """
    Mark a survey as skipped and increment student's missed count
    
    Request Body (JSON):
        student_id (str): Student's unique identifier
        week (int): Week number (1-52)
        year (int): Academic year
    
    Returns:
        200: Survey marked as skipped successfully
        400: Invalid input (missing fields)
        404: Student not found
        409: Survey already completed or already skipped
    """
    try:
        # Parse request
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
            
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        required_fields = ['student_id', 'week', 'year']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        student_id = data['student_id']
        week = data['week']
        year = data['year']
        
        survey_service = current_app.container.survey_service()
        
        survey_service.process_skip(
            student_id=student_id,
            week=week,
            year=year
        )
        
        return jsonify({
            'message': 'Survey marked as skipped',
            'student_id': student_id,
            'week': week,
            'year': year
        }), 200
        
    except ValueError as e:
        error_msg = str(e)
        
        if 'not found' in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        elif 'already completed' in error_msg.lower() or 'already skipped' in error_msg.lower():
            return jsonify({'error': error_msg}), 409
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@survey_bp.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint for survey service
    
    Returns:
        200: Service is healthy
    """
    return jsonify({
        'status': 'ok',
        'service': 'surveys'
    }), 200


@survey_bp.route('/dashboard', methods=['GET'])
@login_required
def student_dashboard():
    """
    Render the student dashboard with radar chart data
    """
    if current_user.role != 'STUDENT':
        return render_template('403.html'), 403
    
    # Fetch student record to get full name
    student_repo = current_app.container.student_repository()
    student = student_repo.get_by_student_id(current_user.username)
    student_name = student.name if student else current_user.username
    
    # Fetch student metrics with cohort averages for radar chart
    chart_data = None
    try:
        analytics_service = current_app.container.analytics_service()
        chart_data = analytics_service.get_student_metrics_with_cohort(current_user.username)
        current_app.logger.info(f"Chart data loaded successfully for {current_user.username}")
    except Exception as e:
        # Log the error for debugging
        current_app.logger.error(f"Failed to load chart data for {current_user.username}: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        
    return render_template('student_dashboard.html', chart_data=chart_data, student_name=student_name)


@survey_bp.route('/new', methods=['GET'])
@login_required
def get_survey_form():
    """
    Render the survey form
    """
    if current_user.role != 'STUDENT':
        return render_template('403.html'), 403
        
    # TODO: Fetch current academic week/year dynamically
    return render_template('student_survey.html', week=1, year=2023)