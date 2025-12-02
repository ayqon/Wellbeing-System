import pytest
from unittest.mock import MagicMock, patch
from flask import Flask
from src.api.admin import admin_bp

class TestAdminAPI:
    @pytest.fixture
    def app(self):
        app = Flask(__name__)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.container = MagicMock()
        app.secret_key = 'test_secret'
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_list_users(self, client, app):
        app.container.admin_service.return_value.get_all_users.return_value = []
        
        with patch('src.api.admin.render_template') as mock_render:
            mock_render.return_value = 'users'
            response = client.get('/admin/users')
            assert response.status_code == 200
            mock_render.assert_called_with('admin_users.html', users=[], active_tab='users')

    def test_settings_view(self, client, app):
        app.container.admin_service.return_value.get_academic_year_config.return_value = {}
        
        with patch('src.api.admin.render_template') as mock_render:
            mock_render.return_value = 'settings'
            response = client.get('/admin/settings')
            assert response.status_code == 200
            mock_render.assert_called_with('admin_settings.html', config={}, active_tab='settings')

    def test_import_view(self, client):
        with patch('src.api.admin.render_template') as mock_render:
            mock_render.return_value = 'import'
            response = client.get('/admin/import')
            assert response.status_code == 200
            mock_render.assert_called_with('admin_import.html', active_tab='import')

    def test_create_user_success(self, client, app):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/create', data={
                'username': 'newuser',
                'password': 'password',
                'role': 'STUDENT'
            })
            
            assert response.status_code == 200
            app.container.admin_service.return_value.create_user.assert_called_once()

    def test_create_user_missing_fields(self, client):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/create', data={
                'username': 'newuser'
            })
            
            assert response.status_code == 200

    def test_create_user_error(self, client, app):
        app.container.admin_service.return_value.create_user.side_effect = ValueError("User exists")
        
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/create', data={
                'username': 'newuser',
                'password': 'password',
                'role': 'STUDENT'
            })
            
            assert response.status_code == 200

    def test_delete_user_success(self, client, app):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/delete', data={
                'user_id': '1'
            })
            
            assert response.status_code == 200
            app.container.admin_service.return_value.hard_delete_user.assert_called_once_with('1')

    def test_update_settings_success(self, client, app):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/settings/update', data={
                'start_date': '2023-09-01',
                'end_date': '2024-06-30'
            })
            
            assert response.status_code == 200
            app.container.admin_service.return_value.set_academic_year.assert_called_once()

    def test_create_user_generic_exception(self, client, app):
        app.container.admin_service.return_value.create_user.side_effect = Exception("DB Error")
        
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/create', data={
                'username': 'newuser',
                'password': 'password',
                'role': 'STUDENT'
            })
            
            assert response.status_code == 200

    def test_delete_user_missing_id(self, client):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/delete', data={})
            
            assert response.status_code == 200

    def test_delete_user_exception(self, client, app):
        app.container.admin_service.return_value.hard_delete_user.side_effect = Exception("Delete Error")
        
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/delete', data={'user_id': '1'})
            
            assert response.status_code == 200

    def test_update_settings_missing_dates(self, client):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/settings/update', data={'start_date': '2023-09-01'})
            
            assert response.status_code == 200

    def test_update_settings_value_error(self, client, app):
        app.container.admin_service.return_value.set_academic_year.side_effect = ValueError("Invalid dates")
        
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/settings/update', data={
                'start_date': '2023-09-01',
                'end_date': '2024-06-30'
            })
            
            assert response.status_code == 200

    def test_update_settings_exception(self, client, app):
        app.container.admin_service.return_value.set_academic_year.side_effect = Exception("System Error")
        
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/settings/update', data={
                'start_date': '2023-09-01',
                'end_date': '2024-06-30'
            })
            
            assert response.status_code == 200

    def test_bulk_delete_users_success(self, client, app):
        app.container.admin_service.return_value.bulk_delete_users.return_value = {'success': 2, 'errors': 0}
        
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/delete-bulk', data={
                'user_ids': ['1', '2']
            })
            
            assert response.status_code == 200
            app.container.admin_service.return_value.bulk_delete_users.assert_called_once()

    def test_bulk_delete_users_no_selection(self, client):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            
            response = client.post('/admin/users/delete-bulk')
            
            assert response.status_code == 200

    def test_import_users_no_file(self, client):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            response = client.post('/admin/import/users')
            assert response.status_code == 200

    def test_import_academic_no_file(self, client):
        with patch('src.api.admin.redirect') as mock_redirect:
            mock_redirect.return_value = 'redirected'
            response = client.post('/admin/import/academic')
            assert response.status_code == 200
