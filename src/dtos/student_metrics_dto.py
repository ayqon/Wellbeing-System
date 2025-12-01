from dataclasses import dataclass
from typing import Optional

@dataclass
class StudentMetricsDTO:
    student_id: str
    grades: Optional[float] = None
    attendance_rate: Optional[float] = None
    engagement_score: Optional[float] = None
    risk_score: Optional[float] = None
