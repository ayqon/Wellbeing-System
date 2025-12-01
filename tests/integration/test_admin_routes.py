import pytest
from flask import Flask
from src.api.admin import admin_bp
from src.services.import_service import ImportService
from unittest.mock import MagicMock

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    # Inject mock service if needed, or patch it
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_import_route(client):
    # The admin route is currently a placeholder
    response = client.get('/admin/import')
    assert response.status_code == 200
    assert b"Import Users Placeholder" in response.data
