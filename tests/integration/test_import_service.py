import pytest
import io
from src.services.import_service import ImportService
from src.models.user import User
from src.models.student import Student
from src.models.academic import ModuleGrade, AttendanceRegister, Module, Course, StudentModule
from datetime import datetime

from src.repositories.user_repository import UserRepository
from src.repositories.student_repository import StudentRepository
from src.utils.parsers import UserCSVParser

@pytest.fixture
def import_service(db_session):
    """
    Fixture to provide an instance of ImportService with injected dependencies.
    
    Args:
        db_session: The SQLAlchemy session fixture.
        
    Returns:
        ImportService: An initialized service instance with real repositories and parser.
    """
    user_repo = UserRepository(db_session)
    student_repo = StudentRepository(db_session)
    parser = UserCSVParser()
    return ImportService(user_repo, student_repo, parser)

def test_process_user_csv_valid(import_service, db_session):
    """
    Test the successful import of a valid user CSV file.
    
    Scenario:
    - A CSV with two valid users (Alice and Bob) is provided.
    - The service should parse the CSV and create corresponding User and Student records.
    
    Assertions:
    - Result success count should be 2.
    - User 'alice' should exist in the database with role 'student'.
    - Student 'S12345' should exist with correct name and email.
    """
    csv_content = "username,password_hash,role,student_id,name,email\n" \
                  "alice,password123,student,S12345,Alice Smith,alice@example.com\n" \
                  "bob,password456,student,S67890,Bob Jones,bob@example.com"
    file_stream = io.StringIO(csv_content)
    
    results = import_service.process_user_csv(file_stream)
    
    # Verify processing results
    assert results["success"] == 2
    assert results["errors"] == 0
    
    # Verify Alice User record
    alice_user = db_session.query(User).filter_by(username="alice").first()
    assert alice_user is not None
    assert alice_user.role == "student"
    
    # Verify Alice Student record
    alice_student = db_session.query(Student).filter_by(student_id="S12345").first()
    assert alice_student is not None
    assert alice_student.name == "Alice Smith"
    assert alice_student.email == "alice@example.com"

def test_process_user_csv_invalid_format(import_service):
    """
    Test that the service raises a ValueError when the CSV is missing required columns.
    
    Scenario:
    - A CSV missing the 'password' and 'student_id' columns is provided.
    
    Assertions:
    - ValueError should be raised with a message indicating missing columns.
    """
    csv_content = "username,role\n" \
                  "alice,student"
    file_stream = io.StringIO(csv_content)
    
    with pytest.raises(ValueError, match="Missing required columns"):
        import_service.process_user_csv(file_stream)

def test_process_academic_csv_grades(import_service, db_session):
    """
    Test the successful import of academic grade data.
    
    Scenario:
    - Pre-requisite: A Student and a Module exist in the database.
    - A CSV containing a grade record for the student and module is provided.
    
    Assertions:
    - Result success count should be 1.
    - A ModuleGrade record should be created with the correct grade value.
    """
    # Setup: Create Student and Module
    student = Student(student_id="S12345", name="Alice", email="alice@test.com")
    course = Course(course_code="CS101", name="Comp Sci")
    module = Module(module_code="M101", name="Intro to CS", course=course)
    db_session.add(student)
    db_session.add(course)
    db_session.add(module)
    db_session.commit()
    
    csv_content = "student_id,module_code,type,value,date\n" \
                  "S12345,M101,grade,85,2023-10-01"
    file_stream = io.StringIO(csv_content)
    
    results = import_service.process_academic_csv(file_stream)
    
    assert results["success"] == 1
    
    # Verify Grade record
    grade = db_session.query(ModuleGrade).first()
    assert grade is not None
    assert grade.grade == 85
    assert grade.student_id == student.id
    assert grade.module_id == module.id

def test_process_academic_csv_attendance(import_service, db_session):
    """
    Test the successful import of academic attendance data.
    
    Scenario:
    - Pre-requisite: A Student and a Module exist in the database.
    - A CSV containing an attendance record is provided.
    
    Assertions:
    - Result success count should be 1.
    - An AttendanceRegister record should be created with the correct status and date.
    """
    # Setup
    student = Student(student_id="S12345", name="Alice", email="alice@test.com")
    course = Course(course_code="CS101", name="Comp Sci")
    module = Module(module_code="M101", name="Intro to CS", course=course)
    db_session.add(student)
    db_session.add(course)
    db_session.add(module)
    db_session.commit()
    
    csv_content = "student_id,module_code,type,value,date\n" \
                  "S12345,M101,attendance,Present,2023-10-01"
    file_stream = io.StringIO(csv_content)
    
    results = import_service.process_academic_csv(file_stream)
    
    assert results["success"] == 1
    
    # Verify Attendance record
    attendance = db_session.query(AttendanceRegister).first()
    assert attendance is not None
    assert attendance.status == "Present"
    assert attendance.date == datetime(2023, 10, 1)
