import pytest
from unittest.mock import MagicMock
from src.app import create_app

class TestApp:
    @pytest.fixture
    def app(self):
        app = create_app()
        app.container = MagicMock()
        return app

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {"status": "ok"}

    def test_load_user(self, app):
        # Access the load_user function registered with login_manager
        # It's a bit tricky to access directly, but we can trigger it via Flask-Login
        # Or we can inspect the login_manager callback if accessible
        
        # Alternative: Simulate a request that requires user loading?
        # Or just manually call the callback if we can find it.
        
        # Let's try to find the callback in login_manager
        print(f"Extensions: {app.extensions.keys()}")
        # Usually it's 'login_manager' or similar if not 'flask_login'
        # But let's check what's available
        if 'flask_login' in app.extensions:
             login_manager = app.extensions['flask_login'].login_manager
        else:
             # Try to find it by type or guess key
             # For now, let's just fail with debug info
             pass
        
        # Actually, let's try to access the user loader via the app's login manager instance if we can find it
        # But since we can't easily get the instance created inside create_app, we rely on extensions.
        
        # If we can't find it, we might need to refactor create_app to expose it or use a different test strategy.
        # But let's see the keys first.
        login_manager = app.login_manager # Flask-Login < 0.6 might attach here? No.
        # It seems Flask-Login 0.6+ uses app.extensions['flask_login'] which is the LoginManager instance itself?
        # Let's check.
        user_loader = login_manager._user_callback
        
        # Mock repo
        mock_user = MagicMock()
        app.container.user_repository.return_value.get.return_value = mock_user
        
        # Call the loader within app context
        with app.app_context():
            user = user_loader("123")
        
        assert user == mock_user
        app.container.user_repository.return_value.get.assert_called_with("123")

    def test_index_redirect(self, client):
        """Test that index redirects to login"""
        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert '/auth/login' in response.location

