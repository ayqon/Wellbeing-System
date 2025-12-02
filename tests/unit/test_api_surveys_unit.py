import pytest
from unittest.mock import MagicMock, PropertyMock, patch
from flask import Flask
from src.api.surveys import survey_bp

class TestSurveyAPI:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.register_blueprint(survey_bp, url_prefix='/surveys')
        app.container = MagicMock()
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_submit_survey_success(self, client, app):
        app.container.survey_service.return_value.submit_response.return_value = MagicMock(
            survey_id=1, student_id="s1", week=1, year=2023, stress=1, sleep=7.5, is_critical=False, status=MagicMock(value="COMPLETED")
        )
        
        response = client.post('/surveys/submit', json={
            'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': 7.5
        })
        
        assert response.status_code == 201

    def test_submit_survey_invalid_json(self, client):
        response = client.post('/surveys/submit', data="invalid json")
        assert response.status_code == 400

    def test_submit_survey_missing_fields(self, client):
        response = client.post('/surveys/submit', json={'student_id': 's1'})
        assert response.status_code == 400

    def test_submit_survey_student_not_found(self, client, app):
        app.container.survey_service.return_value.submit_response.side_effect = ValueError("Student not found")
        
        response = client.post('/surveys/submit', json={
            'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': 8
        })
        
        assert response.status_code == 404

    def test_submit_survey_already_completed(self, client, app):
        app.container.survey_service.return_value.submit_response.side_effect = ValueError("Survey already completed")
        
        response = client.post('/surveys/submit', json={
            'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': 8
        })
        
        assert response.status_code == 409

    def test_submit_survey_generic_error(self, client, app):
        app.container.survey_service.return_value.submit_response.side_effect = Exception("DB Error")
        
        response = client.post('/surveys/submit', json={
            'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': 8
        })
        
        assert response.status_code == 500

    def test_skip_survey_success(self, client, app):
        response = client.post('/surveys/skip', json={
            'student_id': 's1', 'week': 1, 'year': 2023
        })
        assert response.status_code == 200

    def test_submit_survey_empty_json(self, client):
        response = client.post('/surveys/submit', json={})
        assert response.status_code == 400

    def test_submit_survey_status_exception(self, client, app):
        # Mock survey object that raises exception on status access
        mock_survey = MagicMock()
        type(mock_survey).status = PropertyMock(side_effect=Exception("Status access error"))
        # Set other attributes to avoid attribute errors
        mock_survey.survey_id = 1
        mock_survey.student_id = "s1"
        mock_survey.week = 1
        mock_survey.year = 2023
        mock_survey.stress = 1
        mock_survey.sleep = 8
        mock_survey.is_critical = False
        
        app.container.survey_service.return_value.submit_response.return_value = mock_survey
        
        response = client.post('/surveys/submit', json={
            'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': 8
        })
        
        assert response.status_code == 201
        assert response.json['survey']['status'] is None

    def test_skip_survey_empty_json(self, client):
        response = client.post('/surveys/skip', json={})
        assert response.status_code == 400

    def test_skip_survey_value_error(self, client, app):
        app.container.survey_service.return_value.process_skip.side_effect = ValueError("Generic Value Error")
        
        response = client.post('/surveys/skip', json={
            'student_id': 's1', 'week': 1, 'year': 2023
        })
        
        assert response.status_code == 400

    def test_submit_survey_status_none(self, client, app):
        # Mock survey object with None status
        mock_survey = MagicMock()
        mock_survey.status = None
        # Set other attributes
        mock_survey.survey_id = 1
        mock_survey.student_id = "s1"
        mock_survey.week = 1
        mock_survey.year = 2023
        mock_survey.stress = 1
        mock_survey.sleep = 8
        mock_survey.is_critical = False
        
        app.container.survey_service.return_value.submit_response.return_value = mock_survey
        
        response = client.post('/surveys/submit', json={
            'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': 8
        })
        
        assert response.status_code == 201
        assert response.json['survey']['status'] is None

    def test_skip_survey_generic_exception(self, client, app):
        app.container.survey_service.return_value.process_skip.side_effect = Exception("Generic Error")
        
        response = client.post('/surveys/skip', json={
            'student_id': 's1', 'week': 1, 'year': 2023
        })
        
        assert response.status_code == 500

    def test_student_dashboard_success(self, client, app):
        with patch('flask_login.utils._get_user') as mock_current_user:
            mock_user = MagicMock()
            mock_user.role = 'STUDENT'
            mock_current_user.return_value = mock_user
            
            # Mock render_template to avoid template not found error if template is missing
            with patch('src.api.surveys.render_template') as mock_render:
                mock_render.return_value = 'dashboard'
                response = client.get('/surveys/dashboard')
                assert response.status_code == 200
                assert b'dashboard' in response.data

    def test_student_dashboard_forbidden(self, client, app):
        with patch('flask_login.utils._get_user') as mock_current_user:
            mock_user = MagicMock()
            mock_user.role = 'DIRECTOR'
            mock_current_user.return_value = mock_user
            
            with patch('src.api.surveys.render_template') as mock_render:
                mock_render.return_value = '403'
                response = client.get('/surveys/dashboard')
                assert response.status_code == 403

    def test_get_survey_form_success(self, client, app):
        with patch('flask_login.utils._get_user') as mock_current_user:
            mock_user = MagicMock()
            mock_user.role = 'STUDENT'
            mock_current_user.return_value = mock_user
            
            with patch('src.api.surveys.render_template') as mock_render:
                mock_render.return_value = 'survey_form'
                response = client.get('/surveys/new')
                assert response.status_code == 200
                assert b'survey_form' in response.data

    def test_get_survey_form_forbidden(self, client, app):
        with patch('flask_login.utils._get_user') as mock_current_user:
            mock_user = MagicMock()
            mock_user.role = 'DIRECTOR'
            mock_current_user.return_value = mock_user
            
            with patch('src.api.surveys.render_template') as mock_render:
                mock_render.return_value = '403'
                response = client.get('/surveys/new')
                assert response.status_code == 403

    def test_submit_survey_quarter_hour_values(self, client, app):
        """Test that API accepts valid quarter-hour sleep values"""
        quarter_hour_values = [0.0, 0.25, 0.5, 0.75, 7.0, 7.25, 7.5, 7.75, 24.0]
        
        for sleep_value in quarter_hour_values:
            app.container.survey_service.return_value.submit_response.return_value = MagicMock(
                survey_id=1, student_id="s1", week=1, year=2023, stress=1, sleep=sleep_value, is_critical=False, status=MagicMock(value="COMPLETED")
            )
            
            response = client.post('/surveys/submit', json={
                'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': sleep_value
            })
            
            assert response.status_code == 201, f"Failed for sleep value {sleep_value}"

    def test_submit_survey_two_decimal_places(self, client, app):
        """Test that API accepts sleep values with 2 decimal places"""
        app.container.survey_service.return_value.submit_response.return_value = MagicMock(
            survey_id=1, student_id="s1", week=1, year=2023, stress=1, sleep=7.75, is_critical=False, status=MagicMock(value="COMPLETED")
        )
        
        response = client.post('/surveys/submit', json={
            'student_id': 's1', 'week': 1, 'year': 2023, 'stress': 1, 'sleep': 7.75
        })
        
        assert response.status_code == 201
        assert response.json['survey']['sleep'] == 7.75

