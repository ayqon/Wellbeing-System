from sqlalchemy import Column, String, Integer
from src.models.base import BaseModel

class Student(BaseModel):
    __tablename__ = 'students'

    student_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    missed_classes = Column(Integer, default=0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.missed_classes is None:
            self.missed_classes = 0

    def increment_misses(self):
        """Increments the missed_classes counter."""
        self.missed_classes += 1
