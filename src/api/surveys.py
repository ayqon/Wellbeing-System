from flask import Blueprint, request, jsonify, current_app, render_template
from src.models.survey import WellbeingSurvey, SurveyStatus

survey_bp = Blueprint('surveys', __name__)


@survey_bp.route('/dashboard', methods=['GET'])
def student_dashboard():
    # In a real app, we'd fetch the current week/year from a service or config
    week = 5
    year = 2025
    return render_template('student_survey.html', week=week, year=year)


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
        # Parse request - handle JSON parsing errors
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
            
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Extract required fields
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
        
        # Get service from container
        survey_service = current_app.container.survey_service()
        
        # Delegate to service layer
        survey = survey_service.submit_response(
            student_id=student_id,
            week=week,
            year=year,
            stress=stress,
            sleep=sleep
        )
        
        # Build response - handle both real models and mocks
        survey_data = {
            'survey_id': getattr(survey, 'survey_id', None),
            'student_id': getattr(survey, 'student_id', None),
            'week': getattr(survey, 'week', None),
            'year': getattr(survey, 'year', None),
            'stress': getattr(survey, 'stress', None),
            'sleep': getattr(survey, 'sleep', None),
            'is_critical': getattr(survey, 'is_critical', None)
        }
        
        # Handle status separately with maximum safety
        try:
            status = getattr(survey, 'status', None)
            if status is not None:
                # Try to get .value for Enum, otherwise convert to string
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
        
        # Differentiate error types by message content
        if 'not found' in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        elif 'already completed' in error_msg.lower():
            return jsonify({'error': error_msg}), 409
        else:
            # Validation errors (stress/sleep out of range)
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        # Unexpected errors
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
        # Parse request - handle JSON parsing errors
        try:
            data = request.get_json()
        except Exception:
            return jsonify({'error': 'Request body must be valid JSON'}), 400
            
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
        # Extract required fields
        required_fields = ['student_id', 'week', 'year']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return jsonify({
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        student_id = data['student_id']
        week = data['week']
        year = data['year']
        
        # Get service from container
        survey_service = current_app.container.survey_service()
        
        # Delegate to service layer (returns None on success)
        survey_service.process_skip(
            student_id=student_id,
            week=week,
            year=year
        )
        
        # Build response
        return jsonify({
            'message': 'Survey marked as skipped',
            'student_id': student_id,
            'week': week,
            'year': year
        }), 200
        
    except ValueError as e:
        error_msg = str(e)
        
        # Differentiate error types by message content
        if 'not found' in error_msg.lower():
            return jsonify({'error': error_msg}), 404
        elif 'already completed' in error_msg.lower() or 'already skipped' in error_msg.lower():
            return jsonify({'error': error_msg}), 409
        else:
            return jsonify({'error': error_msg}), 400
    
    except Exception as e:
        # Unexpected errors
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