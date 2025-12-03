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
            response = client.post('/admin/import/users', data=data, content_type='multipart/form-data')
            
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')
            app.container.import_service.return_value.process_user_csv.assert_called_once()

    def test_import_users_no_file(self, client, app):
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/users', data={}, content_type='multipart/form-data')
            
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')
            
    def test_import_users_empty_filename(self, client, app):
        data = {
            'file': (io.BytesIO(b""), '')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/users', data=data, content_type='multipart/form-data')
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')

    def test_import_users_partial_success(self, client, app):
        app.container.import_service.return_value.process_user_csv.return_value = {'success': 1, 'errors': 1}
        data = {
            'file': (io.BytesIO(b"username,password"), 'users.csv')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/users', data=data, content_type='multipart/form-data')
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')

    def test_import_users_exception(self, client, app):
        app.container.import_service.return_value.process_user_csv.side_effect = Exception("Processing error")
        data = {
            'file': (io.BytesIO(b"username,password"), 'users.csv')
        }
        with patch('src.api.admin.render_template', return_value='admin_dashboard') as mock_render:
            response = client.post('/admin/import/users', data=data, content_type='multipart/form-data')
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')

    def test_import_grades_success(self, client, app):
        app.container.import_service.return_value.process_grade_csv.return_value = {'success': 1, 'errors': 0}
        data = {'file': (io.BytesIO(b"student_id,module_code,grade"), 'grades.csv')}
        with patch('src.api.admin.render_template', return_value='admin_dashboard'):
            response = client.post('/admin/import/grades', data=data, content_type='multipart/form-data')
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')
            app.container.import_service.return_value.process_grade_csv.assert_called_once()

    def test_import_attendance_success(self, client, app):
        app.container.import_service.return_value.process_attendance_csv.return_value = {'success': 1, 'errors': 0}
        data = {'file': (io.BytesIO(b"student_id,module_code,date,status"), 'attendance.csv')}
        with patch('src.api.admin.render_template', return_value='admin_dashboard'):
            response = client.post('/admin/import/attendance', data=data, content_type='multipart/form-data')
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')
            app.container.import_service.return_value.process_attendance_csv.assert_called_once()

    def test_import_surveys_success(self, client, app):
        app.container.import_service.return_value.process_survey_csv.return_value = {'success': 1, 'errors': 0}
        data = {'file': (io.BytesIO(b"student_id,week,stress,sleep"), 'surveys.csv')}
        with patch('src.api.admin.render_template', return_value='admin_dashboard'):
            response = client.post('/admin/import/surveys', data=data, content_type='multipart/form-data')
            assert response.status_code == 302
            assert response.location.endswith('/admin/import')
            app.container.import_service.return_value.process_survey_csv.assert_called_once()

    def test_download_template_all_types(self, client):
        types = ['users', 'grades', 'attendance', 'surveys']
        for t in types:
            response = client.get(f'/admin/import/template/{t}')
            assert response.status_code == 200
            assert response.headers['Content-Disposition'] == f'attachment; filename=template_{t}.csv'

    def test_download_template_invalid(self, client, app):
        response = client.get('/admin/import/template/invalid')
        assert response.status_code == 400

    def test_import_grades_missing_file(self, client):
        response = client.post('/admin/import/grades')
        assert response.status_code == 302
        assert response.location.endswith('/admin/import')

    def test_import_grades_empty_filename(self, client):
        data = {'file': (io.BytesIO(b""), '')}
        response = client.post('/admin/import/grades', data=data, content_type='multipart/form-data')
        assert response.status_code == 302
        assert response.location.endswith('/admin/import')

    def test_import_grades_service_error(self, client, app):
        app.container.import_service.return_value.process_grade_csv.return_value = {'success': 0, 'errors': 1}
        data = {'file': (io.BytesIO(b"content"), 'test.csv')}
        response = client.post('/admin/import/grades', data=data, content_type='multipart/form-data')
        assert response.status_code == 302

    def test_import_grades_exception(self, client, app):
        app.container.import_service.return_value.process_grade_csv.side_effect = Exception("Processing Error")
        data = {'file': (io.BytesIO(b"content"), 'test.csv')}
        response = client.post('/admin/import/grades', data=data, content_type='multipart/form-data')
        assert response.status_code == 302

    def test_create_user_value_error(self, client, app):
        app.container.admin_service.return_value.create_user.side_effect = ValueError("Invalid Input")
        response = client.post('/admin/users/create', data={'username': 'u', 'password': 'p', 'role': 'r'})
        assert response.status_code == 302

    def test_import_users_service_error(self, client, app):
        app.container.import_service.return_value.process_user_csv.return_value = {'success': 0, 'errors': 1}
        data = {'file': (io.BytesIO(b"content"), 'users.csv')}
        response = client.post('/admin/import/users', data=data, content_type='multipart/form-data')
        assert response.status_code == 302

    def test_delete_user_missing_id(self, client):
        response = client.post('/admin/users/delete', data={})
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')

    def test_delete_user_success(self, client, app):
        response = client.post('/admin/users/delete', data={'user_id': '1'})
        assert response.status_code == 302
        app.container.admin_service.return_value.hard_delete_user.assert_called_once_with('1')

    def test_bulk_delete_users_missing_ids(self, client):
        response = client.post('/admin/users/delete-bulk', data={})
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')

    def test_bulk_delete_users_success(self, client, app):
        app.container.admin_service.return_value.bulk_delete_users.return_value = {'success': 2, 'errors': 0}
        response = client.post('/admin/users/delete-bulk', data={'user_ids': ['1', '2']})
        assert response.status_code == 302
        app.container.admin_service.return_value.bulk_delete_users.assert_called_once()

    def test_update_settings_value_error(self, client, app):
        app.container.admin_service.return_value.set_academic_year.side_effect = ValueError("Invalid dates")
        response = client.post('/admin/settings/update', data={'start_date': '2023-01-01', 'end_date': '2023-12-31'})
        assert response.status_code == 302
        assert response.location.endswith('/admin/settings')
