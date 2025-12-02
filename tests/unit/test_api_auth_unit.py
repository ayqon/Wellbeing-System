import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from src.api.auth import auth_bp

class TestAuthAPI:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.register_blueprint(auth_bp)
        app.container = MagicMock()
        app.secret_key = 'test'
        
        # Register dummy blueprints for redirect targets
        from flask import Blueprint
        surveys_bp = Blueprint('surveys', __name__)
        surveys_bp.add_url_rule('/dashboard', 'student_dashboard', lambda: 'dashboard')
        app.register_blueprint(surveys_bp, url_prefix='/surveys')
        
        analytics_bp = Blueprint('analytics', __name__)
        analytics_bp.add_url_rule('/officer', 'officer_dashboard', lambda: 'officer')
        analytics_bp.add_url_rule('/director', 'director_dashboard', lambda: 'director')
        app.register_blueprint(analytics_bp, url_prefix='/analytics')
        
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_login_get(self, client):
        with patch('src.api.auth.render_template', return_value='login_page'):
            response = client.get('/login')
            assert response.status_code == 200

    def test_login_post_json_success(self, client, app):
        app.container.auth_service.return_value.login.return_value = "token"
        response = client.post('/login', json={'username': 'u', 'password': 'p'})
        assert response.status_code == 200
        assert response.json['token'] == "token"

    def test_login_missing_creds(self, client):
        with patch('src.api.auth.render_template', return_value='login_page'):
            response = client.post('/login', json={})
            assert response.status_code == 400

    def test_login_invalid_creds(self, client, app):
        app.container.auth_service.return_value.login.return_value = None
        with patch('src.api.auth.render_template', return_value='login_page'):
            response = client.post('/login', json={'username': 'u', 'password': 'p'})
            assert response.status_code == 401

    def test_login_exception(self, client, app):
        app.container.auth_service.return_value.login.side_effect = Exception("Error")
        response = client.post('/login', json={'username': 'u', 'password': 'p'})
        assert response.status_code == 500

    def test_logout(self, client):
        with patch('flask_login.logout_user'):
            response = client.get('/logout')
            assert response.status_code == 302

    def test_login_post_form_success_student(self, client, app):
        app.container.auth_service.return_value.login.return_value = "token"
        
        mock_user = MagicMock()
        mock_user.role = 'STUDENT'
        app.container.user_repository.return_value.get_by_username.return_value = mock_user
        
        with patch('src.api.auth.render_template', return_value='login_page') as mock_render, \
             patch('flask_login.login_user'):
            response = client.post('/login', data={'username': 'u', 'password': 'p'}, content_type='application/x-www-form-urlencoded')
            
            # Debug info
            print(f"Login called: {app.container.auth_service.return_value.login.call_args}")
            print(f"Render called: {mock_render.call_args}")
            
            assert response.status_code == 302, f"Expected 302, got {response.status_code}. Render called: {mock_render.called}"
            assert '/surveys/dashboard' in response.headers['Location']

    def test_login_post_form_success_officer(self, client, app):
        app.container.auth_service.return_value.login.return_value = "token"
        
        mock_user = MagicMock()
        mock_user.role = 'OFFICER'
        app.container.user_repository.return_value.get_by_username.return_value = mock_user
        
        with patch('src.api.auth.render_template', return_value='login_page') as mock_render, \
             patch('flask_login.login_user'):
            response = client.post('/login', data={'username': 'u', 'password': 'p'}, content_type='application/x-www-form-urlencoded')
            assert response.status_code == 302, f"Expected 302, got {response.status_code}. Render called: {mock_render.called}"
            assert '/analytics/officer' in response.headers['Location']

    def test_login_post_form_invalid_creds(self, client, app):
        app.container.auth_service.return_value.login.return_value = None
        
        with patch('src.api.auth.render_template', return_value='login_page') as mock_render:
            response = client.post('/login', data={'username': 'u', 'password': 'p'}, content_type='application/x-www-form-urlencoded')
            assert response.status_code == 200
            mock_render.assert_called_with('login.html')

    def test_login_post_form_missing_creds(self, client, app):
        with patch('src.api.auth.render_template', return_value='login_page') as mock_render:
            response = client.post('/login', data={'username': ''}, content_type='application/x-www-form-urlencoded')
            assert response.status_code == 200
            mock_render.assert_called_with('login.html')
            # Verify flash message if possible

    def test_login_post_form_success_director(self, client, app):
        app.container.auth_service.return_value.login.return_value = "token"
        
        mock_user = MagicMock()
        mock_user.role = 'DIRECTOR'
        app.container.user_repository.return_value.get_by_username.return_value = mock_user
        
        with patch('src.api.auth.render_template', return_value='login_page') as mock_render, \
             patch('flask_login.login_user'):
            response = client.post('/login', data={'username': 'u', 'password': 'p'}, content_type='application/x-www-form-urlencoded')
            assert response.status_code == 302
            assert '/analytics/director' in response.headers['Location']

    def test_login_post_form_success_fallback(self, client, app):
        app.container.auth_service.return_value.login.return_value = "token"
        
        mock_user = MagicMock()
        mock_user.role = 'UNKNOWN'
        app.container.user_repository.return_value.get_by_username.return_value = mock_user
        
        with patch('src.api.auth.render_template', return_value='login_page') as mock_render, \
             patch('flask_login.login_user'):
            response = client.post('/login', data={'username': 'u', 'password': 'p'}, content_type='application/x-www-form-urlencoded')
            assert response.status_code == 302
            assert '/analytics/officer' in response.headers['Location']
