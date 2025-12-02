import pytest
from src.models.user import User

@pytest.mark.e2e
class TestAdminFlow:
    def test_admin_ui_journey(self, client, db_session):
        """
        E2E Flow for Admin:
        1. Login as Admin (Mocked/Bypassed via session or direct access if no auth yet)
        2. Access Dashboard (redirects to Users)
        3. Add New User via UI
        4. Verify User in List
        5. Update Settings
        """
        
        # 1. Setup Admin User
        admin = User(username="admin", role="DIRECTOR") # Director has admin access
        admin.set_password("admin123")
        db_session.add(admin)
        db_session.commit()
        
        # Mock Login (if using Flask-Login, we can use test_client to login or mock current_user)
        # For this test, we'll assume we can access routes directly or use a helper if auth is enforced.
        # If auth is enforced, we need to login.
        # Let's try to login if the route exists, otherwise we might need to mock.
        # Based on previous analysis, /auth/login might exist but maybe not fully wired for all tests.
        # Let's assume we can use the client to post to login.
        
        # login_response = client.post('/auth/login', data={'username': 'admin', 'password': 'admin123'})
        # assert login_response.status_code == 200 or login_response.status_code == 302
        
        # If login is not fully implemented in this environment, we might need to rely on 
        # `current_user` mocking or `login_user` helper if available.
        # Given the context, let's try to just access the routes. If they are protected, 
        # we might need to mock `flask_login.login_required`.
        
        # For E2E using Flask Client, we can use `with client.session_transaction() as sess:` to set user_id
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin.id)
            sess['_fresh'] = True

        # 2. Access Dashboard
        resp = client.get('/admin/dashboard', follow_redirects=True)
        assert resp.status_code == 200
        assert b'User Management' in resp.data
        
        # 3. Add New User
        # First get the add page
        resp = client.get('/admin/users/add')
        assert resp.status_code == 200
        assert b'Add New User' in resp.data
        
        # Post new user
        new_user_data = {
            'username': 'new_teacher',
            'password': 'password123',
            'role': 'OFFICER',
            'first_name': 'New',
            'last_name': 'Teacher'
        }
        resp = client.post('/admin/users/create', data=new_user_data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'User new_teacher created successfully' in resp.data
        
        # 4. Verify User in List
        assert b'new_teacher' in resp.data
        assert b'OFFICER' in resp.data
        
        # 5. Update Settings
        # Get settings page
        resp = client.get('/admin/settings')
        assert resp.status_code == 200
        
        # Update settings
        settings_data = {
            'start_date': '2024-09-01',
            'end_date': '2025-06-01'
        }
        resp = client.post('/admin/settings/update', data=settings_data, follow_redirects=True)
        assert resp.status_code == 200
        assert b'Academic year settings updated' in resp.data
        
        # Verify persistence (optional, but good for E2E)
        resp = client.get('/admin/settings')
        assert b'2024-09-01' in resp.data
