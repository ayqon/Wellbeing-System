from src.repositories.survey_repository import SurveyRepository
from src.repositories.student_repository import StudentRepository
from src.models.survey import WellbeingSurvey, SurveyStatus


class SurveyService:
    """
    Service class for managing student wellbeing surveys
    
    OOP Principles: Dependency Injection, Encapsulation
    Business Rules:
    - Students can submit surveys with stress (1-5) and sleep (0-24)
    - Skipping surveys increments consecutive_misses counter
    - Completing surveys resets consecutive_misses to 0
    - Cannot skip or resubmit an already completed survey
    """
    
    # Configuration constants
    STRESS_MIN = 1
    STRESS_MAX = 5
    SLEEP_MIN = 0
    SLEEP_MAX = 24
    CRITICAL_STRESS_THRESHOLD = 4
    CRITICAL_SLEEP_THRESHOLD = 4
    
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
        
        Business Logic:
        1. Verify student exists
        2. Check if survey already exists for this week
        3. Create SKIPPED survey record
        4. Increment student's consecutive_misses counter
        
        Args:
            student_id: Student's unique identifier
            week: Week number of the academic year (1-52)
            year: Academic year
        
        Raises:
            ValueError: If student not found or survey already exists
        """
        # Validate student exists
        student = self.student_repo.get_by_student_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Check for existing survey
        existing_survey = self.survey_repo.get_by_student_week(student_id, week, year)
        if existing_survey:
            if existing_survey.status == SurveyStatus.COMPLETED:
                raise ValueError(
                    f"Cannot skip: Survey already completed for student {student_id}, "
                    f"week {week}, year {year}"
                )
            elif existing_survey.status == SurveyStatus.SKIPPED:
                raise ValueError(
                    f"Survey already skipped for student {student_id}, "
                    f"week {week}, year {year}"
                )
        
        # Create skipped survey and increment misses in transaction
        # Note: Actual transaction implementation depends on your repository layer
        survey = WellbeingSurvey(
            student_id=student_id,
            week=week,
            year=year,
            status=SurveyStatus.SKIPPED,
            is_critical=False
        )
        self.survey_repo.add(survey)
        
        student.increment_misses()
        self.student_repo.update(student)
    
    def submit_response(self, student_id: str, week: int, year: int, 
                       stress: int, sleep: int) -> WellbeingSurvey:
        """
        Submit a wellbeing survey response
        
        Business Logic:
        1. Validate inputs (stress: 1-5, sleep: 0-24)
        2. Verify student exists
        3. Check if survey already completed (prevent duplicates)
        4. Create or update survey with COMPLETED status
        5. Reset student's consecutive_misses counter
        6. Mark as critical if thresholds exceeded
        
        Args:
            student_id: Student's unique identifier
            week: Week number (1-52)
            year: Academic year
            stress: Stress level (1-5, where 5=highest)
            sleep: Sleep hours (0-24)
        
        Returns:
            Saved WellbeingSurvey object
        
        Raises:
            ValueError: If validation fails or survey already completed
        """
        # Input validation
        if not (self.STRESS_MIN <= stress <= self.STRESS_MAX):
            raise ValueError(
                f"Stress must be {self.STRESS_MIN}-{self.STRESS_MAX}, got {stress}"
            )
        if not (self.SLEEP_MIN <= sleep <= self.SLEEP_MAX):
            raise ValueError(
                f"Sleep must be {self.SLEEP_MIN}-{self.SLEEP_MAX} hours, got {sleep}"
            )
        
        # Validate student exists
        student = self.student_repo.get_by_student_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")
        
        # Check existing survey
        survey = self.survey_repo.get_by_student_week(student_id, week, year)
        
        if survey:
            if survey.status == SurveyStatus.COMPLETED:
                raise ValueError(
                    f"Survey already completed for student {student_id}, "
                    f"week {week}, year {year}. Cannot resubmit."
                )
            # If SKIPPED, we allow them to complete it (upgrade from SKIPPED to COMPLETED)
        else:
            # Create new survey
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
        
        # Save survey and reset misses
        if survey.survey_id:  # Existing survey (was SKIPPED)
            self.survey_repo.update(survey)
        else:  # New survey
            self.survey_repo.add(survey)
        
        # Reset consecutive misses since survey completed
        student.reset_misses()
        self.student_repo.update(student)
        
        return survey
    
    def _check_critical(self, stress: int, sleep: int) -> bool:
        """
        Check if wellbeing metrics indicate critical status requiring attention
        
        Args:
            stress: Stress level (1-5)
            sleep: Sleep hours (0-24)
        
        Returns:
            True if either:
            - Stress >= 4 (high stress)
            - Sleep <= 4 hours (severe sleep deprivation)
        """
        return stress >= self.CRITICAL_STRESS_THRESHOLD or sleep <= self.CRITICAL_SLEEP_THRESHOLD