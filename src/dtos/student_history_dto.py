from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class WellbeingRecord:
    """Single wellbeing survey record"""
    week: int
    year: int
    stress: Optional[int]
    sleep: Optional[int]
    is_critical: bool
    status: str
    created_at: datetime


@dataclass
class StudentHistoryDTO:
    """
    Student history with chronological wellbeing data
    
    This DTO encapsulates historical wellbeing data for a student.
    Immutable and type-safe.
    """
    student_id: str
    name: str
    email: str
    
    # Historical wellbeing data (chronologically ordered)
    wellbeing_history: List[WellbeingRecord]
    
    # Computed statistics
    total_surveys_completed: int
    total_surveys_skipped: int
    average_stress: Optional[float]
    average_sleep: Optional[float]