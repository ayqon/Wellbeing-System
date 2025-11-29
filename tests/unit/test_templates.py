import pytest
from flask import Flask, render_template
from unittest.mock import MagicMock

def test_student_detail_template():
    app = Flask(__name__, template_folder="../src/templates")
    
    # Create mock objects
    mock_user = MagicMock()
    mock_user.name = "John Doe"
    mock_user.email = "john.doe@example.com"
    
    mock_student = MagicMock()
    mock_student.student_id = "S12345"
    mock_student.course_code = "CS101"
    mock_student.current_risk_score = 0.85
    mock_student.consecutive_misses = 3
    mock_student.user = mock_user
    
    with app.app_context():
        rendered = render_template("student_detail.html", student=mock_student)
        
        assert "John Doe" in rendered
        assert "john.doe@example.com" in rendered
        assert "S12345" in rendered
        assert "CS101" in rendered
        assert "0.85" in rendered
        assert "3" in rendered
        print("Template rendered successfully with object attributes!")

if __name__ == "__main__":
    test_student_detail_template()
