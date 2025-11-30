import pytest
from src.models.user import User
from src.models.student import Student
from src.models.course import Course
from src.services.token_service import TokenService

def get_auth_headers(user_id, role):
    token = TokenService.create_token(user_id, role)
    return {"Authorization": f"Bearer {token}"}

def test_get_correlations_director(client, db_session):
    # Setup
    director = User(user_id="dir1", username="director1", password_hash="hash", roles=["DIRECTOR"])
    db_session.add(director)
    
    # Create a course assigned to director
    course = Course(course_code="CS101", title="CS Intro", director_user_id="dir1")
    db_session.add(course)
    
    # Create students in that course
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0)
    s1.user = User(user_id="s1", username="student1", password_hash="hash", roles=["STUDENT"])
    db_session.add(s1)
    
    s2 = Student(student_id="s2", course_code="CS102", current_risk_score=20.0) # Different course
    s2.user = User(user_id="s2", username="student2", password_hash="hash", roles=["STUDENT"])
    db_session.add(s2)
    
    db_session.commit()
    
    # Action
    headers = get_auth_headers("dir1", "DIRECTOR")
    response = client.get("/analytics/correlations", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["risk_score"] == 80.0
    assert "username" not in data[0] # Anonymized

def test_get_risk_list_officer(client, db_session):
    # Setup
    officer = User(user_id="off1", username="officer1", password_hash="hash", roles=["OFFICER"])
    db_session.add(officer)
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0)
    s1.user = User(user_id="s1", username="student1", first_name="John", last_name="Doe", password_hash="hash", roles=["STUDENT"])
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers("off1", "OFFICER")
    response = client.get("/analytics/risk-list", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["student_id"] == "s1"
    assert data[0]["username"] == "John Doe"
    assert data[0]["risk_score"] == 80.0

def test_get_academic_list_director(client, db_session):
    # Setup
    director = User(user_id="dir1", username="director1", password_hash="hash", roles=["DIRECTOR"])
    db_session.add(director)
    course = Course(course_code="CS101", title="CS Intro", director_user_id="dir1")
    db_session.add(course)
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0)
    s1.user = User(user_id="s1", username="student1", first_name="John", last_name="Doe", password_hash="hash", roles=["STUDENT"])
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers("dir1", "DIRECTOR")
    response = client.get("/analytics/academic-list", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]["username"] == "John Doe" # Pseudonymized (restored name)
    assert "risk_score" not in data[0] # No risk score

def test_get_academic_stats_director(client, db_session):
    # Setup
    director = User(user_id="dir1", username="director1", password_hash="hash", roles=["DIRECTOR"])
    db_session.add(director)
    course = Course(course_code="CS101", title="CS Intro", director_user_id="dir1")
    db_session.add(course)
    
    s1 = Student(student_id="s1", course_code="CS101")
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers("dir1", "DIRECTOR")
    response = client.get("/analytics/academic-stats", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert "courses" in data
    assert "modules" in data

def test_get_student_details_officer(client, db_session):
    # Setup
    officer = User(user_id="off1", username="officer1", password_hash="hash", roles=["OFFICER"])
    db_session.add(officer)
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0)
    s1.user = User(user_id="s1", username="student1", password_hash="hash", roles=["STUDENT"])
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers("off1", "OFFICER")
    response = client.get("/analytics/student/s1", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert data["student_id"] == "s1"
    assert data["risk_score"] == 80.0

def test_get_student_details_director_privacy(client, db_session):
    # Setup
    director = User(user_id="dir1", username="director1", password_hash="hash", roles=["DIRECTOR"])
    db_session.add(director)
    
    s1 = Student(student_id="s1", course_code="CS101", current_risk_score=80.0)
    s1.user = User(user_id="s1", username="student1", password_hash="hash", roles=["STUDENT"])
    db_session.add(s1)
    db_session.commit()
    
    # Action
    headers = get_auth_headers("dir1", "DIRECTOR")
    response = client.get("/analytics/student/s1", headers=headers)
    
    # Assert
    assert response.status_code == 200
    data = response.json
    assert data["student_id"] == "s1"
    assert "risk_score" not in data # Filtered out
