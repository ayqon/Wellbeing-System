from sqlalchemy.orm import Session
from typing import Optional
from src.repositories.base import SqlAlchemyRepository
from src.models.student import Student

class StudentRepository(SqlAlchemyRepository[Student]):
    """
    Repository for Student entities.
    Inherits from SqlAlchemyRepository to provide standard CRUD operations.
    """
    def __init__(self, session: Session):
        """
        Initialize the StudentRepository.

        Args:
            session (Session): The SQLAlchemy database session.
        """
        super().__init__(session, Student)
    
    def get_by_student_id(self, student_id: str) -> Optional[Student]:
        """
        Retrieve a student by their student_id field (not primary key).

        Args:
            student_id (str): The student's unique identifier

        Returns:
            Optional[Student]: The student if found, otherwise None
        """
        return self.session.query(Student).filter_by(student_id=student_id).first()