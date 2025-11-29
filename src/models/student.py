from sqlalchemy import Column, String, Integer
from src.models.base import BaseModel, TimestampMixin


class Student(BaseModel, TimestampMixin):
    """
    Student entity
    
    OOP Principle: Encapsulation - Business logic is encapsulated within the class
    """
    __tablename__ = 'students'

    # Primary key - manually added since BaseModel is empty
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Business fields
    student_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    missed_surveys = Column(Integer, default=0)

    def __init__(self, **kwargs):
        """
        Initialize a Student object
        
        Args:
            **kwargs: Keyword arguments for student fields
        """
        super().__init__(**kwargs)
        if self.missed_surveys is None:
            self.missed_surveys = 0

    def increment_misses(self):
        """
        Increments the missed_surveys counter
        
        OOP Principle: Encapsulation - Logic is contained within the object
        """
        self.missed_surveys += 1
    
    def reset_misses(self):
        """Resets the missed_surveys counter"""
        self.missed_surveys = 0

    def __repr__(self):
        """String representation for debugging purposes"""
        return f"<Student {self.student_id}: {self.name}>"