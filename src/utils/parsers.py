import csv
from abc import ABC, abstractmethod
from typing import List, Any
from dataclasses import dataclass
from src.models.user import User

@dataclass
class RawModuleGrade:
    student_id: str
    module_code: str
    grade: float

class AbstractParser(ABC):
    @abstractmethod
    def parse(self, file_stream) -> List[Any]:
        """Parses a file stream and returns a list of objects."""
        pass

class UserCSVParser(AbstractParser):
    def parse(self, file_stream) -> List[User]:
        reader = csv.DictReader(file_stream)
        users = []
        for row in reader:
            # Handle potential missing keys gracefully or let it error if strict
            # Assuming strict CSV structure matching the model needs
            users.append(User(
                username=row['username'],
                # email=row['email'], # User model doesn't have email
                password_hash=row['password_hash'],
                role=row.get('role', 'student') # Default to student if not present
            ))
        return users

class GradeCSVParser(AbstractParser):
    def parse(self, file_stream) -> List[RawModuleGrade]:
        reader = csv.DictReader(file_stream)
        grades = []
        for row in reader:
            grades.append(RawModuleGrade(
                student_id=row['student_id'],
                module_code=row['module_code'],
                grade=float(row['grade'])
            ))
        return grades
