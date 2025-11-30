import pytest
from unittest.mock import Mock, patch
from flask import Flask
from src.api.surveys import survey_bp
from src.models.survey import WellbeingSurvey, SurveyStatus


@pytest.fixture
def app():
    """Create Flask app with survey blueprint for testing"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Mock container
    mock_container = Mock()
    mock_survey_service = Mock()
    mock_container.survey_service.return_value = mock_survey_service
    app.container = mock_container
    
    # Register blueprint
    app.register_blueprint(survey_bp, url_prefix='/api/surveys')
    
    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


class TestSurveySubmitEndpoint:
    """Test POST /api/surveys/submit endpoint"""
    
    def test_submit_survey_success(self, client, app):
        """Test successful survey submission"""
        # Arrange
        mock_survey = Mock(spec=WellbeingSurvey)
        mock_survey.survey_id = 1
        mock_survey.student_id = "12345"
        mock_survey.week = 10
        mock_survey.year = 2025
        mock_survey.stress = 3
        mock_survey.sleep = 7
        mock_survey.status = SurveyStatus.COMPLETED
        mock_survey.is_critical = False
        
        app.container.survey_service().submit_response.return_value = mock_survey
        
        # Act
        response = client.post('/api/surveys/submit', json={
            'student_id': '12345',
            'week': 10,
            'year': 2025,
            'stress': 3,
            'sleep': 7
        })
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Survey submitted successfully'
        assert data['survey']['survey_id'] == 1
        assert data['survey']['student_id'] == '12345'
        assert data['survey']['stress'] == 3
        assert data['survey']['sleep'] == 7
        assert data['survey']['is_critical'] is False
    
    def test_submit_survey_missing_required_fields(self, client):
        """Test submit with missing required fields returns 400"""
        response = client.post('/api/surveys/submit', json={
            'student_id': '12345',
            'week': 10
            # Missing: year, stress, sleep
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    def test_submit_survey_invalid_stress_value(self, client, app):
        """Test submit with invalid stress value"""
        app.container.survey_service().submit_response.side_effect = ValueError(
            "Stress must be 1-5, got 10"
        )
        
        response = client.post('/api/surveys/submit', json={
            'student_id': '12345',
            'week': 10,
            'year': 2025,
            'stress': 10,
            'sleep': 7
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Stress must be 1-5' in data['error']
    
    def test_submit_survey_invalid_sleep_value(self, client, app):
        """Test submit with invalid sleep value"""
        app.container.survey_service().submit_response.side_effect = ValueError(
            "Sleep must be 0-24 hours, got 25"
        )
        
        response = client.post('/api/surveys/submit', json={
            'student_id': '12345',
            'week': 10,
            'year': 2025,
            'stress': 3,
            'sleep': 25
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Sleep must be 0-24' in data['error']
    
    def test_submit_survey_student_not_found(self, client, app):
        """Test submit for non-existent student"""
        app.container.survey_service().submit_response.side_effect = ValueError(
            "Student 99999 not found"
        )
        
        response = client.post('/api/surveys/submit', json={
            'student_id': '99999',
            'week': 10,
            'year': 2025,
            'stress': 3,
            'sleep': 7
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_submit_survey_already_completed(self, client, app):
        """Test resubmitting an already completed survey"""
        app.container.survey_service().submit_response.side_effect = ValueError(
            "Survey already completed for student 12345, week 10, year 2025. Cannot resubmit."
        )
        
        response = client.post('/api/surveys/submit', json={
            'student_id': '12345',
            'week': 10,
            'year': 2025,
            'stress': 3,
            'sleep': 7
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'already completed' in data['error'].lower()
    
    def test_submit_survey_invalid_json(self, client):
        """Test submit with invalid JSON body"""
        response = client.post('/api/surveys/submit', 
                              data='not valid json',
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestSurveySkipEndpoint:
    """Test POST /api/surveys/skip endpoint"""
    
    def test_skip_survey_success(self, client, app):
        """Test successful survey skip"""
        # Mock service - process_skip returns None on success
        app.container.survey_service().process_skip.return_value = None
        
        response = client.post('/api/surveys/skip', json={
            'student_id': '12345',
            'week': 10,
            'year': 2025
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Survey marked as skipped'
        assert data['student_id'] == '12345'
        assert data['week'] == 10
        assert data['year'] == 2025
        
        # Verify service was called correctly
        app.container.survey_service().process_skip.assert_called_once_with(
            student_id='12345',
            week=10,
            year=2025
        )
    
    def test_skip_survey_missing_fields(self, client):
        """Test skip with missing required fields"""
        response = client.post('/api/surveys/skip', json={
            'student_id': '12345'
            # Missing: week, year
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'required' in data['error'].lower()
    
    def test_skip_survey_student_not_found(self, client, app):
        """Test skip for non-existent student"""
        app.container.survey_service().process_skip.side_effect = ValueError(
            "Student 99999 not found"
        )
        
        response = client.post('/api/surveys/skip', json={
            'student_id': '99999',
            'week': 10,
            'year': 2025
        })
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    def test_skip_survey_already_completed(self, client, app):
        """Test skip when survey already completed"""
        app.container.survey_service().process_skip.side_effect = ValueError(
            "Cannot skip: Survey already completed for student 12345, week 10, year 2025"
        )
        
        response = client.post('/api/surveys/skip', json={
            'student_id': '12345',
            'week': 10,
            'year': 2025
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'already completed' in data['error'].lower()
    
    def test_skip_survey_already_skipped(self, client, app):
        """Test skip when survey already skipped"""
        app.container.survey_service().process_skip.side_effect = ValueError(
            "Survey already skipped for student 12345, week 10, year 2025"
        )
        
        response = client.post('/api/surveys/skip', json={
            'student_id': '12345',
            'week': 10,
            'year': 2025
        })
        
        assert response.status_code == 409
        data = response.get_json()
        assert 'error' in data
        assert 'already skipped' in data['error'].lower()
    
    def test_skip_survey_invalid_json(self, client):
        """Test skip with invalid JSON body"""
        response = client.post('/api/surveys/skip',
                              data='not valid json',
                              content_type='application/json')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestSurveyHealthEndpoint:
    """Test GET /api/surveys/health endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/surveys/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'ok'
        assert data['service'] == 'surveys'