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

def test_import_route(client, monkeypatch):
    # Mock ImportService.execute_import
    mock_service = MagicMock()
    mock_service.execute_import.return_value = {"status": "success"}
    
    # Patch the service used in the blueprint (assuming it's instantiated there or imported)
    # For this test, we'll assume the blueprint uses a global instance or we patch the class
    monkeypatch.setattr("src.api.admin.import_service.execute_import", mock_service.execute_import)

    import io
    data = {
        'file': (io.BytesIO(b'my file contents'), 'test.csv')
    }
    
    response = client.post('/admin/import', data=data)
    
    assert response.status_code == 200
    assert response.json == {"status": "success"}
    mock_service.execute_import.assert_called_once()
