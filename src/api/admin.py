from flask import Blueprint, request, jsonify
from src.services.import_service import ImportService
from src.core.database import Database
from src.repositories.user_repository import UserRepository
from src.repositories.student_repository import StudentRepository
from src.utils.parsers import UserCSVParser

admin_bp = Blueprint('admin', __name__)

# Instantiate dependencies
# In a real app, this would be handled by a DI container
db = Database()
session = next(db.get_db()) # Get a session
user_repo = UserRepository(session)
student_repo = StudentRepository(session)
user_parser = UserCSVParser()

import_service = ImportService(user_repo, student_repo, user_parser)

@admin_bp.route('/import', methods=['POST'])
def import_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            # Pass the file stream directly
            # Note: request.files['file'] is a FileStorage object which behaves like a file stream
            result = import_service.execute_import(file.stream)
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    return jsonify({"error": "Unknown error"}), 500
