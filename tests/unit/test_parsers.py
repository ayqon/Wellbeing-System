import pytest
import io
from src.utils.parsers import UserCSVParser, GradeCSVParser, RawModuleGrade
from src.models.user import User

def test_user_csv_parser():
    # Note: User model no longer has email, and has role.
    csv_content = "username,password_hash,role,student_id,name,email\njdoe,hashed_secret,student,S123,John Doe,jdoe@test.com"
    file_stream = io.StringIO(csv_content)
    
    parser = UserCSVParser()
    users = parser.parse(file_stream)
    
    assert len(users) == 1
    assert isinstance(users[0], dict)
    assert users[0]['username'] == "jdoe"
    assert users[0]['password_hash'] == "hashed_secret"
    assert users[0]['role'] == "student"
    assert users[0]['student_id'] == "S123"

def test_grade_csv_parser():
    csv_content = "student_id,module_code,grade\nS12345,CS101,85.5"
    file_stream = io.StringIO(csv_content)
    
    parser = GradeCSVParser()
    grades = parser.parse(file_stream)
    
    assert len(grades) == 1
    assert isinstance(grades[0], RawModuleGrade)
    assert grades[0].student_id == "S12345"
    assert grades[0].module_code == "CS101"
    assert grades[0].grade == 85.5
