from src.repositories.survey_repository import SurveyRepository
from src.repositories.student_repository import StudentRepository
from src.models.survey import WellbeingSurvey, SurveyStatus


class SurveyService:
    """
    Service class for managing student wellbeing surveys
    
    OOP Principles: Dependency Injection, Encapsulation
    """
    
    def __init__(self, survey_repo: SurveyRepository, student_repo: StudentRepository):
        """
        Initialize SurveyService with repository dependencies
        
        Args:
            survey_repo: Repository for survey operations
            student_repo: Repository for student operations
        """
        self.survey_repo = survey_repo
        self.student_repo = student_repo
    
    def process_skip(self, student_id: str, week: int, year: int) -> None:
        """
        Process a student skipping a survey
        
        Args:
            student_id: Student's unique identifier (e.g., "12345")
            week: Week number of the academic year
            year: Academic year
        
        Raises:
            ValueError: If student not found
        """
        # Get student by student_id
        student = self.student_repo.get_by_student_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Get or create survey record
        survey = self.survey_repo.get_by_student_week(student_id, week, year)
        if not survey:
            survey = WellbeingSurvey(
                student_id=student_id,
                week=week,
                year=year,
                status=SurveyStatus.SKIPPED,
                is_critical=False
            )
            self.survey_repo.create(survey)
        else:
            # if the survey is completed
            raise ValueError(
                f"Survey already exists for student {student_id}, "
                f"week {week}, year {year}"
            )
        
        # Increment student's consecutive misses
        student.increment_misses()
        self.student_repo.save(student)
    
    def submit_response(self, student_id: str, week: int, year: int, 
                       stress: int, sleep: int) -> WellbeingSurvey:
        """
        Submit a wellbeing survey response
        
        Args:
            student_id: Student's unique identifier
            week: Week number
            year: Academic year
            stress: Stress level (0-10)
            sleep: Sleep hours
        
        Returns:
            Saved WellbeingSurvey object
        """
        # Get or create survey
        survey = self.survey_repo.get_by_student_week(student_id, week, year)
        if not survey:
            survey = WellbeingSurvey(
                student_id=student_id,
                week=week,
                year=year
            )
        
        # Update survey fields
        survey.status = SurveyStatus.COMPLETED
        survey.stress = stress
        survey.sleep = sleep
        survey.is_critical = self._check_critical(stress, sleep)
        
        # Save survey
        if survey.survey_id:  # Existing survey
            self.survey_repo.save(survey)
        else:  # New survey
            self.survey_repo.create(survey)
        
        # Reset student's consecutive misses since they completed a survey
        student = self.student_repo.get_by_student_id(student_id)
        if student:
            student.reset_misses()
            self.student_repo.save(student)
        
        return survey
    
    def _check_critical(self, stress: int, sleep: int) -> bool:
        """
        Check if wellbeing metrics indicate critical status
        
        Args:
            stress: Stress level (0-10)
            sleep: Sleep hours
        
        Returns:
            True if critical (needs attention)
        """
        return stress >= 8 or sleep <= 4