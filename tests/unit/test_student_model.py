import pytest
from src.models.student import Student

def test_student_initialization():
    student = Student(name="John Doe", email="john@example.com", student_id="S12345")
    assert student.name == "John Doe"
    assert student.email == "john@example.com"
    assert student.student_id == "S12345"
    assert student.missed_classes == 0

def test_increment_misses():
    student = Student(name="Jane Soe", email="jane@example.com", student_id="S67890")
    assert student.missed_classes == 0
    student.increment_misses()
    assert student.missed_classes == 1
    student.increment_misses()
    assert student.missed_classes == 2


