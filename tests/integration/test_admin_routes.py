import pytest
from flask import Flask
from src.api.admin import admin_bp
from src.services.import_service import ImportService
from unittest.mock import MagicMock

@pytest.fixture
def app():
    # Point to the correct template folder
    import os
    from flask_login import LoginManager
    
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/templates'))
    app = Flask(__name__, template_folder=template_dir)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.secret_key = 'test' # Needed for flash
    
    # Setup Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return None # Anonymous user
    
    # Register dummy auth blueprint
    from flask import Blueprint
    auth_bp = Blueprint('auth', __name__)
    auth_bp.add_url_rule('/login', 'login', lambda: 'login')
    auth_bp.add_url_rule('/logout', 'logout', lambda: 'logout')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_import_route(client):
    # The admin route now renders the dashboard
    response = client.get('/admin/import')
    assert response.status_code == 200
    assert b"Admin Dashboard" in response.data
