import pytest
from src.models.user import User
from src.models.student import Student
from src.models.academic import Course
from src.services.token_service import TokenService

def get_auth_headers(user_id, role):
    token = TokenService.create_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}

def test_get_correlations_director(client, db_session):
    # Setup
    director = User(username="director1", password_hash="hash", role="DIRECTOR")
    db_session.add(director)
    db_session.flush() # Get ID
    
    course = Course(course_code="CS101", name="CS Intro", director_user_id=director.id)
    db_session.add(course)
    
    # Create students in that course
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0, name="Student One", email="s1@test.com")
    s1.user = User(username="student1", password_hash="hash", role="STUDENT")
    db_session.add(s1)
    
    s2 = Student(student_id="s2", course_code="CS102", current_risk_score=20.0, name="Student Two", email="s2@test.com")
    s2.user = User(username="student2", password_hash="hash", role="STUDENT")
    db_session.add(s2)
    
    db_session.commit()
    
    # Action
    headers = get_auth_headers(str(director.id), "DIRECTOR")
    response = client.get("/analytics/correlations", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["risk_score"] == 80.0
    assert "username" not in data[0] or data[0]["username"] is None # Anonymized

def test_get_risk_list_officer(client, db_session):
    # Setup
    officer = User(username="officer1", password_hash="hash", role="OFFICER")
    db_session.add(officer)
    db_session.flush()
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0, name="Student One", email="s1@test.com")
    s1.user = User(username="student1", password_hash="hash", role="STUDENT")
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers(str(officer.id), "OFFICER")
    response = client.get("/analytics/risk-list", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["student_id"] == "s1"
    assert data[0]["username"] == "Student One"
    assert data[0]["risk_score"] == 34.0
    assert "grade" in data[0]
    assert "attendance" in data[0]

def test_get_academic_list_director(client, db_session):
    # Setup
    director = User(username="director2", password_hash="hash", role="DIRECTOR") # Unique username
    db_session.add(director)
    db_session.flush()
    
    course = Course(course_code="CS101", name="CS Intro", director_user_id=director.id)
    db_session.add(course)
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0, name="Student One", email="s1_academic@test.com") # Unique email
    s1.user = User(username="student1_academic", password_hash="hash", role="STUDENT") # Unique username
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers(str(director.id), "DIRECTOR")
    response = client.get("/analytics/academic-list", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["username"] == "Student One" # Should match Student name
    assert "risk_score" not in data[0] # No risk score

def test_get_academic_stats_director(client, db_session):
    # Setup
    director = User(username="director1", password_hash="hash", role="DIRECTOR")
    db_session.add(director)
    db_session.flush()
    
    course = Course(course_code="CS101", name="CS Intro", director_user_id=director.id)
    db_session.add(course)
    
    s1 = Student(student_id="s1", course_code="CS101", name="Student One", email="s1@test.com")
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers(str(director.id), "DIRECTOR")
    response = client.get("/analytics/academic-stats", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert "courses" in data
    assert "modules" in data

def test_get_student_details_officer(client, db_session):
    # Setup
    officer = User(username="officer1", password_hash="hash", role="OFFICER")
    db_session.add(officer)
    db_session.flush()
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0, name="Student One", email="s1@test.com")
    s1.user = User(username="student1", password_hash="hash", role="STUDENT")
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers(str(officer.id), "OFFICER")
    response = client.get("/analytics/student/s1", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert data["student_id"] == "s1"
    assert data["risk_score"] == 80.0

def test_get_student_details_director_privacy(client, db_session):
    # Setup
    director = User(username="director1", password_hash="hash", role="DIRECTOR")
    db_session.add(director)
    db_session.flush()
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0, name="Student One", email="s1@test.com")
    s1.user = User(username="student1", password_hash="hash", role="STUDENT")
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers(str(director.id), "DIRECTOR")
    response = client.get("/analytics/student/s1", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert data["student_id"] == "s1"
    assert "risk_score" not in data # Filtered out
