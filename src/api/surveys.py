from flask import Blueprint, request, jsonify, current_app
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