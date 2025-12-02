import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from src.api.analytics import analytics_bp

class TestAnalyticsAPI:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.register_blueprint(analytics_bp)
        app.container = MagicMock()
        app.secret_key = 'test'
        
        # Setup dummy templates
        from jinja2 import DictLoader
        app.jinja_env.loader = DictLoader({
            'officer_dashboard.html': 'officer_dashboard',
            'director_dashboard.html': 'director_dashboard',
            'student_detail.html': 'student_detail'
        })
        
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_officer_dashboard_success(self, client, app):
        app.container.analytics_service.return_value.get_officer_snapshot.return_value = []
        response = client.get('/officer/dashboard')
        assert response.status_code == 200
        assert b'officer_dashboard' in response.data

    def test_officer_dashboard_error(self, client, app):
        app.container.analytics_service.return_value.get_officer_snapshot.side_effect = Exception("Error")
        response = client.get('/officer/dashboard')
        assert response.status_code == 200
        assert b'officer_dashboard' in response.data

    def test_director_dashboard_success(self, client, app):
        app.container.analytics_service.return_value.get_director_view.return_value = []
        response = client.get('/director/dashboard')
        assert response.status_code == 200
        assert b'director_dashboard' in response.data

    def test_director_dashboard_error(self, client, app):
        app.container.analytics_service.return_value.get_director_view.side_effect = Exception("Error")
        response = client.get('/director/dashboard')
        assert response.status_code == 200
        assert b'director_dashboard' in response.data

    def test_get_student_detail_success(self, client, app):
        app.container.analytics_service.return_value.get_student_history.return_value = MagicMock(wellbeing_history=[])
        app.container.student_repository.return_value.get_by_student_id.return_value = MagicMock()
        
        response = client.get('/student/s1/detail')
        assert response.status_code == 200
        assert b'student_detail' in response.data

    def test_get_student_detail_error(self, client, app):
        app.container.analytics_service.return_value.get_student_history.side_effect = Exception("Error")
        response = client.get('/student/s1/detail')
        assert response.status_code == 500

    def test_get_correlations_success(self, client, app):
        app.container.analytics_service.return_value.get_director_view.return_value = []
        response = client.get('/correlations')
        assert response.status_code == 200

    def test_get_correlations_error(self, client, app):
        app.container.analytics_service.return_value.get_director_view.side_effect = Exception("Error")
        response = client.get('/correlations')
        assert response.status_code == 500

    def test_get_risk_list_success(self, client, app):
        app.container.analytics_service.return_value.get_officer_snapshot.return_value = []
        response = client.get('/risk-list')
        assert response.status_code == 200

    def test_get_risk_list_error(self, client, app):
        app.container.analytics_service.return_value.get_officer_snapshot.side_effect = Exception("Error")
        response = client.get('/risk-list')
        assert response.status_code == 500

    def test_get_academic_list_unauthorized(self, client):
        response = client.get('/academic-list')
        assert response.status_code == 401

    def test_get_academic_list_officer(self, client, app):
        repo_mock = MagicMock()
        student_mock = MagicMock()
        student_mock.student_id = "s1"
        student_mock.name = "n1"
        student_mock.course_code = "CS101"
        repo_mock.list.return_value = [student_mock]
        app.container.student_repository.return_value = repo_mock
        
        import src.api.analytics as analytics_module
        with patch.object(analytics_module.TokenService, 'verify_token', return_value={'role': 'OFFICER', 'sub': 'o1'}):
            response = client.get('/academic-list', headers={'Authorization': 'Bearer token'})
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]['course'] == "CS101"

    def test_get_academic_list_director_no_course(self, client, app):
        # Mock DB Session for Course lookup - return None
        session_mock = MagicMock()
        session_mock.query.return_value.filter_by.return_value.first.return_value = None
        app.container.db.SessionLocal.return_value = session_mock

        import src.api.analytics as analytics_module
        with patch.object(analytics_module.TokenService, 'verify_token', return_value={'role': 'DIRECTOR', 'sub': 'd1'}):
            response = client.get('/academic-list', headers={'Authorization': 'Bearer token'})
            assert response.status_code == 200
            assert response.json == []

    def test_get_academic_list_forbidden(self, client, app):
        import src.api.analytics as analytics_module
        with patch.object(analytics_module.TokenService, 'verify_token', return_value={'role': 'STUDENT', 'sub': 's1'}):
            response = client.get('/academic-list', headers={'Authorization': 'Bearer token'})
            assert response.status_code == 403

    def test_get_academic_list_director(self, client, app):
        # Mock Repo
        repo_mock = MagicMock()
        student_mock = MagicMock()
        student_mock.student_id = "s1"
        student_mock.name = "n1"
        student_mock.course_code = "CS101"
        repo_mock.list.return_value = [student_mock]
        app.container.student_repository.return_value = repo_mock
        
        # Mock DB Session for Course lookup
        session_mock = MagicMock()
        course_mock = MagicMock()
        course_mock.course_code = "CS101"
        session_mock.query.return_value.filter_by.return_value.first.return_value = course_mock
        app.container.db.SessionLocal.return_value = session_mock

        import src.api.analytics as analytics_module
        with patch.object(analytics_module.TokenService, 'verify_token', return_value={'role': 'DIRECTOR', 'sub': 'd1'}):
            response = client.get('/academic-list', headers={'Authorization': 'Bearer token'})
            assert response.status_code == 200
            assert len(response.json) == 1
            assert response.json[0]['course'] == "CS101"

    def test_get_academic_stats(self, client):
        response = client.get('/academic-stats')
        assert response.status_code == 200

    def test_get_student_details_unauthorized(self, client):
        response = client.get('/student/s1')
        assert response.status_code == 403

    def test_get_student_details_officer(self, client, app):
        repo_mock = MagicMock()
        student_mock = MagicMock()
        student_mock.student_id = "s1"
        student_mock.current_risk_score = 50
        repo_mock.get_by_student_id.return_value = student_mock
        app.container.student_repository.return_value = repo_mock
        
        import src.api.analytics as analytics_module
        with patch.object(analytics_module.TokenService, 'verify_token', return_value={'role': 'OFFICER'}):
            response = client.get('/student/s1', headers={'Authorization': 'Bearer token'})
            assert response.status_code == 200, f"Status: {response.status_code}, Data: {response.data}"
            assert 'risk_score' in response.json

    def test_get_student_details_director(self, client, app):
        repo_mock = MagicMock()
        student_mock = MagicMock()
        student_mock.student_id = "s1"
        repo_mock.get_by_student_id.return_value = student_mock
        app.container.student_repository.return_value = repo_mock
        
        import src.api.analytics as analytics_module
        with patch.object(analytics_module.TokenService, 'verify_token', return_value={'role': 'DIRECTOR'}):
            response = client.get('/student/s1', headers={'Authorization': 'Bearer token'})
            assert response.status_code == 200, f"Status: {response.status_code}, Data: {response.data}"
            assert 'risk_score' not in response.json

    def test_get_student_details_not_found(self, client, app):
        repo_mock = MagicMock()
        repo_mock.get_by_student_id.return_value = None
        app.container.student_repository.return_value = repo_mock
        
        import src.api.analytics as analytics_module
        with patch.object(analytics_module.TokenService, 'verify_token', return_value={'role': 'OFFICER'}):
            response = client.get('/student/s1', headers={'Authorization': 'Bearer token'})
            assert response.status_code == 404, f"Status: {response.status_code}, Data: {response.data}"

