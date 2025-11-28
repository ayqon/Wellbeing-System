# from sqlalchemy import Column, String, Integer
# from src.models.base import BaseModel

# class Student(BaseModel):
#     __tablename__ = 'students'

#     student_id = Column(String, unique=True, nullable=False)
#     name = Column(String, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     missed_classes = Column(Integer, default=0)

#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         if self.missed_classes is None:
#             self.missed_classes = 0

#     def increment_misses(self):
#         """Increments the missed_classes counter."""
#         self.missed_classes += 1

from sqlalchemy import Column, String, Integer, DateTime
from datetime import datetime, timezone
from src.models.base import BaseModel


class Student(BaseModel):
    """
    Student entity
    
    OOP Principle: Encapsulation - Business logic is encapsulated within the class
    """
    __tablename__ = 'students'

    # Primary key - manually added since BaseModel is empty
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps - track when record is created and updated
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )

    # Business fields
    student_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    missed_classes = Column(Integer, default=0)

    def __init__(self, **kwargs):
        """
        Initialize a Student object
        
        Args:
            **kwargs: Keyword arguments for student fields
        """
        super().__init__(**kwargs)
        if self.missed_classes is None:
            self.missed_classes = 0

    def increment_misses(self):
        """
        Increments the missed_classes counter
        
        OOP Principle: Encapsulation - Logic is contained within the object
        """
        self.missed_classes += 1

    def __repr__(self):
        """String representation for debugging purposes"""
        return f"<Student {self.student_id}: {self.name}>"