import pytest
from unittest.mock import Mock, patch
from flask import Flask
from flask_login import UserMixin
from src.api.surveys import survey_bp

class MockUser(UserMixin):
    def __init__(self, username, role):
        self.username = username
        self.role = role
        self.id = username

@pytest.fixture
def app():
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.register_blueprint(survey_bp)
    app.config['SECRET_KEY'] = 'test'
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_container(app):
    container = Mock()
    app.container = container
    return container

def test_student_dashboard_chart_error(client, app, mock_container):
    # Mock current_user
    with client.session_transaction() as sess:
        sess['_user_id'] = 'student1'
        
    # Mock login manager
    with patch('flask_login.utils._get_user') as mock_get_user:
        mock_get_user.return_value = MockUser('student1', 'STUDENT')
        
        # Mock analytics service to raise exception
        mock_analytics = Mock()
        mock_analytics.get_student_metrics_with_cohort.side_effect = Exception("Chart Error")
        mock_container.analytics_service.return_value = mock_analytics
        
        # Mock student repository
        mock_repo = Mock()
        mock_student = Mock()
        mock_student.name = 'student1'
        mock_repo.get_by_student_id.return_value = mock_student
        mock_container.student_repository.return_value = mock_repo
        
        # Mock logger
        app.logger = Mock()
        
        # Mock render_template
        with patch('src.api.surveys.render_template') as mock_render:
            mock_render.return_value = 'rendered_template'
            
            # Execute
            response = client.get('/dashboard')
            
            # Verify
            assert response.status_code == 200
            # Verify error was logged
            app.logger.error.assert_called()
            # Verify template was rendered
            mock_render.assert_called_with('student_dashboard.html', chart_data=None, student_name='student1')
