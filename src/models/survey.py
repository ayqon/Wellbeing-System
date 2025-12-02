from sqlalchemy import Column, String, Integer, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship, backref
from src.models.base import BaseModel, TimestampMixin
import enum

class SurveyStatus(enum.Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    SKIPPED = "SKIPPED"

class WellbeingSurvey(BaseModel, TimestampMixin):
    """
    Model representing a weekly wellbeing survey submission.
    """
    __tablename__ = 'wellbeing_surveys'

    survey_id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(String, ForeignKey('students.student_id'), nullable=False)
    week = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum(SurveyStatus), default=SurveyStatus.PENDING)
    stress = Column(Integer, nullable=True)
    sleep = Column(Integer, nullable=True)
    is_critical = Column(Boolean, nullable=False)

    student = relationship("Student", backref=backref("surveys", cascade="all, delete-orphan"))