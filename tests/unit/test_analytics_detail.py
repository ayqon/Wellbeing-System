import pytest
from unittest.mock import Mock, patch
from flask import Flask
from src.api.analytics import analytics_bp

@pytest.fixture
def app():
    import os
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.register_blueprint(analytics_bp)
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

def test_get_student_detail_chart_error(client, app, mock_container):
    # Mock analytics service
    mock_analytics = Mock()
    mock_history = Mock()
    mock_history.wellbeing_history = []
    mock_analytics.get_student_history.return_value = mock_history
    # Raise exception for chart data
    mock_analytics.get_student_metrics_with_cohort.side_effect = Exception("Chart Error")
    mock_container.analytics_service.return_value = mock_analytics
    
    # Mock student repo
    mock_repo = Mock()
    mock_student = Mock()
    mock_student.name = "Test Student"
    mock_student.email = "test@test.com"
    mock_student.student_id = "student1"
    mock_repo.get_by_student_id.return_value = mock_student
    mock_container.student_repository.return_value = mock_repo
    
    # Mock logger
    app.logger = Mock()
    
    # Mock render_template
    with patch('src.api.analytics.render_template') as mock_render:
        mock_render.return_value = 'rendered_template'
        
        # Execute
        response = client.get('/student/student1/detail')
        
        # Verify
        assert response.status_code == 200
        # Verify error was logged
        app.logger.error.assert_called()
        # Verify template was rendered
        mock_render.assert_called()
