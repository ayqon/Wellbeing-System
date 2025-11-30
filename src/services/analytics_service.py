from typing import Optional
from src.repositories.student_repository import StudentRepository
from src.repositories.survey_repository import SurveyRepository
from src.dtos.student_history_dto import (
    StudentHistoryDTO,
    WellbeingRecord
)
from src.models.survey import SurveyStatus

class AnalyticsServiceError(Exception):
    """Base class for analytics-related errors."""
    pass


class AnalyticsService:
    ###* **DI:** Inject `RiskCalculator`, `Anonymizer`, and `StudentRepository`.
    def __init__(self, risk_calculator, anonymizer, student_repo, survey_repo: SurveyRepository = None): 
        self.risk_calculator = risk_calculator
        self.anonymizer = anonymizer
        self.student_repo = student_repo
        self.survey_repo = survey_repo

    ###* **Method:** `get_director_view(course_id)`: Orchestrates data fetch $\to$ anonymization $\to$ risk calc.
    def get_director_view(self, course_id):
        try:
            students = self.student_repo.fetch_by_course(course_id)
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch student data: {e}")

        try:
            anonymized = self.anonymizer.anonymize(students)
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to anonymize data: {e}")

        # Enforce hard privacy
        for s in anonymized:
            s.pop("name", None)
            s.pop("email", None)
            s.pop("student_id", None)
            s["name"] = None
            s["email"] = None
            s["student_id"] = None

        try:
            metrics = self.risk_calculator.calculate(anonymized)
        except Exception as e:
            raise AnalyticsServiceError(f"Risk calculation failed: {e}")

        return metrics
    
    def get_student_history(self, student_id: str) -> StudentHistoryDTO:
        """
        Get chronological wellbeing history for a student
        """
        # Get student by student_id (string)
        try:
            student = self.student_repo.get_by_student_id(student_id)
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch student: {e}")
        
        if not student:
            raise AnalyticsServiceError(f"Student {student_id} not found")
        
        # Get all surveys for this student (chronologically ordered)
        try:
            surveys = self.survey_repo.get_by_student(student_id) if self.survey_repo else []
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch surveys: {e}")
        
        # Transform to DTOs (maintains chronological order from repository)
        wellbeing_history = [
            WellbeingRecord(
                week=survey.week,
                year=survey.year,
                stress=survey.stress,
                sleep=survey.sleep,
                is_critical=survey.is_critical,
                status=survey.status.value,
                created_at=survey.created_at
            )
            for survey in surveys
        ]
        
        # Compute statistics
        completed_surveys = [s for s in surveys if s.status == SurveyStatus.COMPLETED]
        skipped_surveys = [s for s in surveys if s.status == SurveyStatus.SKIPPED]
        
        # Calculate averages only from completed surveys with non-null values
        avg_stress = None
        if completed_surveys:
            stress_values = [s.stress for s in completed_surveys if s.stress is not None]
            if stress_values:
                avg_stress = sum(stress_values) / len(stress_values)
        
        avg_sleep = None
        if completed_surveys:
            sleep_values = [s.sleep for s in completed_surveys if s.sleep is not None]
            if sleep_values:
                avg_sleep = sum(sleep_values) / len(sleep_values)
        
        # Build and return DTO
        return StudentHistoryDTO(
            student_id=student.student_id,
            name=student.name,
            email=student.email,
            wellbeing_history=wellbeing_history,  # Chronologically ordered
            total_surveys_completed=len(completed_surveys),
            total_surveys_skipped=len(skipped_surveys),
            average_stress=avg_stress,
            average_sleep=avg_sleep
        )

