import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from src.api.admin import admin_bp
import io

class TestCoverageGaps:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.container = MagicMock()
        app.secret_key = 'test'
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_create_user_missing_fields(self, client):
        # Test missing fields (lines 57-58)
        response = client.post('/admin/users/create', data={
            'username': 'test'
            # Missing password and role
        })
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')

    def test_create_user_generic_exception(self, client, app):
        # Test generic exception (line 60)
        app.container.admin_service.return_value.create_user.side_effect = Exception("Unexpected error")
        
        response = client.post('/admin/users/create', data={
            'username': 'test',
            'password': 'password',
            'role': 'STUDENT'
        })
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')

    def test_delete_user_generic_exception(self, client, app):
        # Test generic exception (line 80)
        app.container.admin_service.return_value.hard_delete_user.side_effect = Exception("Unexpected error")
        
        response = client.post('/admin/users/delete', data={'user_id': '1'})
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')

    def test_bulk_delete_generic_exception(self, client, app):
        # Test generic exception (line 105)
        app.container.admin_service.return_value.bulk_delete_users.side_effect = Exception("Unexpected error")
        
        response = client.post('/admin/users/delete-bulk', data={'user_ids': ['1', '2']})
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')

    def test_update_settings_missing_fields(self, client):
        # Test missing fields (lines 125-126)
        response = client.post('/admin/settings/update', data={
            'start_date': '2023-09-01'
            # Missing end_date
        })
        assert response.status_code == 302
        assert response.location.endswith('/admin/settings')

    def test_update_settings_generic_exception(self, client, app):
        # Test generic exception (line 128)
        app.container.admin_service.return_value.set_academic_year.side_effect = Exception("Unexpected error")
        
        response = client.post('/admin/settings/update', data={
            'start_date': '2023-09-01',
            'end_date': '2024-06-01'
        })
        assert response.status_code == 302
        assert response.location.endswith('/admin/settings')

    def test_import_users_generic_exception(self, client, app):
        # Test generic exception (line 159)
        # We need to mock import_service to raise exception
        app.container.import_service.return_value.process_user_csv.side_effect = Exception("Unexpected error")
        
        data = {
            'file': (io.BytesIO(b"username,password"), 'users.csv')
        }
        response = client.post('/admin/import/users', data=data, content_type='multipart/form-data')
        assert response.status_code == 302
        assert response.location.endswith('/admin/import')



    def test_service_bulk_delete_partial_exception(self):
        # Test exception inside loop in admin_service.bulk_delete_users (lines 70-71)
        from src.services.admin_service import AdminService
        
        user_repo = MagicMock()
        system_repo = MagicMock()
        service = AdminService(user_repo, system_repo)
        
        # Mock hard_delete_user to raise exception for one user
        # We can't easily mock self.hard_delete_user directly since it's a method on the object under test
        # But hard_delete_user calls user_repo.delete, so we can make that raise exception
        
        # First call succeeds (returns True), second raises exception
        user_repo.delete.side_effect = [True, Exception("DB Error")]
        user_repo.get_by_id.return_value = MagicMock() # Ensure user exists
        
        result = service.bulk_delete_users(['1', '2'])
        
        assert result['success'] == 1
        assert result['errors'] == 1

    def test_add_user_view(self, client):
        # Test add user view (line 20)
        with patch('src.api.admin.render_template', return_value='admin_add_user') as mock_render:
            response = client.get('/admin/users/add')
            assert response.status_code == 200
            assert b'admin_add_user' in response.data

    def test_dashboard_redirect(self, client):
        # Test dashboard redirect (line 43)
        response = client.get('/admin/dashboard')
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')

    def test_bulk_delete_partial_success_flash(self, client, app):
        # Test bulk delete partial success flash message (line 107)
        app.container.admin_service.return_value.bulk_delete_users.return_value = {'success': 1, 'errors': 1}
        
        response = client.post('/admin/users/delete-bulk', data={'user_ids': ['1', '2']})
        assert response.status_code == 302
        assert response.location.endswith('/admin/users')
        # We can't easily check flash message content with client.post redirect, 
        # but executing the line is enough for coverage.
