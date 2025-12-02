import pytest
from unittest.mock import MagicMock
from src.repositories.student_repository import StudentRepository

class TestStudentRepository:
    def test_fetch_by_course(self):
        session = MagicMock()
        repo = StudentRepository(session)
        
        repo.fetch_by_course("C1")
        
        session.query.return_value.filter_by.assert_called_with(course_code="C1")
