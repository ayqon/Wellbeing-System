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
    def parse(self, file_stream) -> List[dict]:
        reader = csv.DictReader(file_stream)
        
        # Validate headers
        required_fields = {'username', 'password_hash', 'student_id', 'name', 'email'}
        if not reader.fieldnames or not required_fields.issubset(set(reader.fieldnames)):
            raise ValueError(f"Missing required columns. Expected: {required_fields}")
            
        users = []
        for row in reader:
            users.append({
                'username': row['username'],
                'password_hash': row['password_hash'],
                'role': row.get('role', 'student'),
                'student_id': row['student_id'],
                'name': row['name'],
                'email': row['email']
            })
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
