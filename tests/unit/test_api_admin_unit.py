import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from src.api.admin import admin_bp
import io

class TestAdminAPI:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.container = MagicMock()
        app.secret_key = 'test'
        
        # Setup dummy templates
        from jinja2 import DictLoader
        app.jinja_env.loader = DictLoader({
            'admin.html': 'admin_dashboard'
        })
        
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_import_users_success(self, client, app):
        app.container.import_service.return_value.process_user_csv.return_value = {'success': 1, 'errors': 0}
        
        data = {
            'file': (io.BytesIO(b"username,password"), 'users.csv')
        }
        
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import', data=data, content_type='multipart/form-data')
            
            assert response.status_code == 200
            assert b'admin_dashboard' in response.data
            app.container.import_service.return_value.process_user_csv.assert_called_once()

    def test_import_users_no_file(self, client, app):
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import', data={}, content_type='multipart/form-data')
            
            assert response.status_code == 400
            # Should flash error and render template (or redirect)
            # For now assuming it renders template with error
            
    def test_import_users_empty_filename(self, client, app):
        data = {
            'file': (io.BytesIO(b""), '')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import', data=data, content_type='multipart/form-data')
            assert response.status_code == 400

    def test_import_users_partial_success(self, client, app):
        app.container.import_service.return_value.process_user_csv.return_value = {'success': 1, 'errors': 1}
        data = {
            'file': (io.BytesIO(b"username,password"), 'users.csv')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import', data=data, content_type='multipart/form-data')
            assert response.status_code == 200
            # Verify flash message content if possible, or just status code

    def test_import_users_exception(self, client, app):
        app.container.import_service.return_value.process_user_csv.side_effect = Exception("Processing error")
        data = {
            'file': (io.BytesIO(b"username,password"), 'users.csv')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import', data=data, content_type='multipart/form-data')
            assert response.status_code == 200 # Renders template with error flash

    def test_import_academic_success(self, client, app):
        app.container.import_service.return_value.process_academic_csv.return_value = {'success': 1, 'errors': 0}
        
        data = {
            'file': (io.BytesIO(b"student_id,module_code"), 'academic.csv')
        }
        
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/academic', data=data, content_type='multipart/form-data')
            
            assert response.status_code == 200
            assert b'admin_dashboard' in response.data
            app.container.import_service.return_value.process_academic_csv.assert_called_once()

    def test_import_academic_no_file(self, client, app):
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/academic', data={}, content_type='multipart/form-data')
            
            assert response.status_code == 400

    def test_import_academic_empty_filename(self, client, app):
        data = {
            'file': (io.BytesIO(b""), '')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/academic', data=data, content_type='multipart/form-data')
            assert response.status_code == 400

    def test_import_academic_partial_success(self, client, app):
        app.container.import_service.return_value.process_academic_csv.return_value = {'success': 1, 'errors': 1}
        data = {
            'file': (io.BytesIO(b"student_id,module_code"), 'academic.csv')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/academic', data=data, content_type='multipart/form-data')
            assert response.status_code == 200

    def test_import_academic_exception(self, client, app):
        app.container.import_service.return_value.process_academic_csv.side_effect = Exception("Processing error")
        data = {
            'file': (io.BytesIO(b"student_id,module_code"), 'academic.csv')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/academic', data=data, content_type='multipart/form-data')
            assert response.status_code == 200
