import pytest
from flask import Flask, render_template
from unittest.mock import MagicMock

import os

def test_student_detail_template():
    # Construct absolute path to templates directory
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/templates"))
    app = Flask(__name__, template_folder=base_dir)
    app.secret_key = 'test'
    
    # Register auth blueprint to support url_for('auth.logout')
    from src.api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Register analytics blueprint to support url_for('analytics.officer_dashboard')
    from src.api.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    
    # Register admin blueprint
    from src.api.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Create mock objects
    mock_user = MagicMock()
    mock_user.name = "John Doe"
    mock_user.email = "john.doe@example.com"
    
    mock_student = MagicMock()
    mock_student.student_id = "S12345"
    mock_student.course_code = "CS101"
    mock_student.current_risk_score = 85.5
    mock_student.consecutive_misses = 3
    mock_student.user = mock_user
    mock_student.name = "John Doe" # Template uses student.name directly
    mock_student.email = "john.doe@example.com" # Template uses student.email directly
    
    @app.context_processor
    def inject_user():
        mock_current_user = MagicMock()
        mock_current_user.is_authenticated = True
        mock_current_user.name = "John Doe"
        return dict(current_user=mock_current_user)

    with app.test_request_context("/"):
        rendered = render_template("student_detail.html", student=mock_student, history=[])
        
        assert "John Doe" in rendered
        assert "john.doe@example.com" in rendered
        assert "S12345" in rendered
        assert "CS101" in rendered
        assert "85.5" in rendered
        assert "3" in rendered
        print("Template rendered successfully with object attributes!")

if __name__ == "__main__":
    test_student_detail_template()
