import pytest
from flask import Flask, request, jsonify
from src.api.validation import Validator
import json

@pytest.fixture
def app():
    app = Flask(__name__)
    
    @app.route('/test/json', methods=['POST'])
    @Validator.validate_json
    def test_json():
        return jsonify({"status": "success"})

    @app.route('/test/required', methods=['POST'])
    @Validator.validate_json
    def test_required():
        data = request.get_json()
        error = Validator.validate_required_fields(data, ['name', 'age'])
        if error:
            return jsonify({"error": error}), 400
        return jsonify({"status": "success"})

    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_validate_json_decorator_success(client):
    response = client.post('/test/json', json={"foo": "bar"})
    assert response.status_code == 200
    assert response.json == {"status": "success"}

def test_validate_json_decorator_failure(client):
    response = client.post('/test/json', data="not json")
    assert response.status_code == 400
    assert "Request must be JSON" in response.json['error']

def test_validate_required_fields_success(client):
    response = client.post('/test/required', json={"name": "Alice", "age": 30})
    assert response.status_code == 200

def test_validate_required_fields_missing(client):
    response = client.post('/test/required', json={"name": "Alice"})
    assert response.status_code == 400
    assert "Missing required field: age" in response.json['error']

class TestValidatorUnit:
    def test_validate_required_fields_empty(self):
        result = Validator.validate_required_fields({}, ['field'])
        assert result == "No data provided"
        
        result = Validator.validate_required_fields(None, ['field'])
        assert result == "No data provided"
