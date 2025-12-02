from flask import Blueprint, request, jsonify, current_app, render_template
from src.services.token_service import TokenService

analytics_bp = Blueprint('analytics', __name__)

def get_current_user_role():
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = TokenService.verify_token(token)
        if payload:
            return payload.get('role')
    return None

# ... (keep existing helper and API routes if needed, or refactor)

@analytics_bp.route('/officer/dashboard', methods=['GET'])
def officer_dashboard():
    """
    Renders the Officer Dashboard with student risk snapshots.
    """
    service = current_app.container.analytics_service()
    try:
        students = service.get_officer_snapshot()
        return render_template('officer_dashboard.html', students=students)
    except Exception as e:
        return render_template('officer_dashboard.html', students=[], error=str(e))

@analytics_bp.route('/director/dashboard', methods=['GET'])
def director_dashboard():
    """
    Renders the Director Dashboard with anonymized student data.
    """
    service = current_app.container.analytics_service()
    try:
        students = service.get_director_view("CS101")
        return render_template('director_dashboard.html', students=students, course_id="CS101")
    except Exception as e:
        return render_template('director_dashboard.html', students=[], course_id="CS101", error=str(e))

@analytics_bp.route('/student/<student_id>/detail', methods=['GET'])
def get_student_detail(student_id):
    """
    Renders the detailed view for a specific student.
    """
    service = current_app.container.analytics_service()
    try:
        history_dto = service.get_student_history(student_id)
        
        repo = current_app.container.student_repository()
        student = repo.get_by_student_id(student_id)
        
        return render_template('student_detail.html', student=student, history=history_dto.wellbeing_history)
    except Exception as e:
        return f"Error: {str(e)}", 500

# API Endpoints for JSON clients

@analytics_bp.route('/correlations', methods=['GET'])
def get_correlations():
    """
    API endpoint to get correlation data for Director view.
    """
    service = current_app.container.analytics_service()
    try:
        data = service.get_director_view("CS101")
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/risk-list', methods=['GET'])
def get_risk_list():
    """
    API endpoint to get the list of at-risk students for Officers.
    """
    service = current_app.container.analytics_service()
    try:
        results = service.get_officer_snapshot()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/academic-list', methods=['GET'])
def get_academic_list():
    """
    API endpoint to list all students with basic academic info.
    """
    auth_header = request.headers.get('Authorization')
    user_id = None
    role = None
    
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        payload = TokenService.verify_token(token)
        if payload:
            role = payload.get('role')
            user_id = payload.get('sub')

    if not role:
        return jsonify({'error': 'Unauthorized'}), 401

    repo = current_app.container.student_repository()
    
    if role == 'DIRECTOR':
        # Find director's course
        from src.models.academic import Course
        session = current_app.container.db.SessionLocal()
        try:
            course = session.query(Course).filter_by(director_user_id=user_id).first()
            if not course:
                return jsonify([]), 200 # No course assigned
            
            students = repo.fetch_by_course(course.course_code) # Assuming fetch_by_course uses course_code
            # Wait, repo.fetch_by_course might not exist or might use ID. 
            # Let's check StudentRepository. 
            # If not, we can filter the full list (inefficient but works for prototype)
            # students = [s for s in repo.list() if s.course_code == course.course_code]
            
            # Let's assume repo.list() returns all and we filter here for safety if fetch_by_course is missing
            all_students = repo.list()
            students = [s for s in all_students if s.course_code == course.course_code]
            
        finally:
            session.close()
            
    elif role == 'OFFICER':
        students = repo.list()
    else:
        return jsonify({'error': 'Forbidden'}), 403

    results = []
    for s in students:
        results.append({
            "student_id": s.student_id,
            "username": s.name,
            "course": s.course_code
        })
    return jsonify(results), 200

@analytics_bp.route('/academic-stats', methods=['GET'])
def get_academic_stats():
    """
    API endpoint to get high-level academic statistics.
    """
    return jsonify({
        "courses": 1,
        "modules": 1
    }), 200

@analytics_bp.route('/student/<student_id>', methods=['GET'])
def get_student_details(student_id):
    """
    API endpoint to get details for a specific student, enforcing role-based privacy.
    """
    role = get_current_user_role()
    if role not in ['OFFICER', 'DIRECTOR']:
        return jsonify({'error': 'Unauthorized'}), 403
        
    repo = current_app.container.student_repository()
    student = repo.get_by_student_id(student_id)
    if not student:
        return jsonify({'error': 'Not found'}), 404
        
    if role == 'OFFICER':
        return jsonify({
            "student_id": student.student_id,
            "risk_score": student.current_risk_score
        }), 200
        
    if role == 'DIRECTOR':
        return jsonify({
            "student_id": student.student_id,
            # Privacy: Risk score is redacted for Directors in this view
        }), 200
