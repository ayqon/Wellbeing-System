from src.repositories.base import BaseRepository
from src.models.student import Student
from sqlalchemy.orm import Session

class StudentRepository(BaseRepository[Student]):
    def __init__(self, session: Session):
        super().__init__(session, Student)