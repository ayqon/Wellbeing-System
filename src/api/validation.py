from flask import request, jsonify
from functools import wraps

class Validator:
    """
    Utility class for API input validation.
    """

    @staticmethod
    def validate_json(f):
        """
        Decorator to ensure the request has a JSON body.
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            return f(*args, **kwargs)
        return decorated_function

    @staticmethod
    def validate_required_fields(data, required_fields):
        """
        Validates that all required fields are present in the data dictionary.
        
        Args:
            data (dict): The data to validate.
            required_fields (list): List of required field names.
            
        Returns:
            str: Error message if validation fails, None otherwise.
        """
        if not data:
             return "No data provided"
             
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"
        return None
