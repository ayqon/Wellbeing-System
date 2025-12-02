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
    def __init__(self, risk_calculator, anonymizer, student_repo, survey_repo: SurveyRepository = None): 
        """
        Initialize AnalyticsService.
        
        Args:
            risk_calculator: Service for calculating risk.
            anonymizer: Service for anonymizing data.
            student_repo: Repository for student data.
            survey_repo: Repository for survey data.
        """
        self.risk_calculator = risk_calculator
        self.anonymizer = anonymizer
        self.student_repo = student_repo
        self.survey_repo = survey_repo

    def _calculate_metrics(self, students):
        """Helper to calculate grade and attendance metrics."""
        from src.models.academic import ModuleGrade, AttendanceRegister
        session = self.student_repo.session
        
        for student in students:
            # 1. Average Grade
            grades = session.query(ModuleGrade).filter_by(student_id=student.id).all()
            if grades:
                avg_grade = sum(g.grade for g in grades) / len(grades)
            else:
                avg_grade = 0.0
            student._temp_grade = avg_grade
            
            # 2. Attendance Percentage
            attendance_records = session.query(AttendanceRegister).filter_by(student_id=student.id).all()
            if attendance_records:
                total_classes = len(attendance_records)
                present_classes = sum(1 for r in attendance_records if r.status == 'Present')
                attendance_pct = (present_classes / total_classes) * 100
            else:
                attendance_pct = 0
            student._temp_attendance = int(attendance_pct)
        return students

    def get_director_risk_view(self, course_id):
        """
        Returns anonymized and shuffled risk data for the Director.
        """
        try:
            students = self.student_repo.fetch_by_course(course_id)
            students = self._calculate_metrics(students)
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
            # Shuffle for additional privacy in Risk View
            import random
            random.shuffle(metrics)
            return metrics
        except Exception as e:
            raise AnalyticsServiceError(f"Risk calculation failed: {e}")

    def get_director_academic_view(self, course_id):
        """
        Returns unanonymized academic data (Name, ID, Grade, Attendance) for the Director.
        NO Risk Scores.
        """
        try:
            students = self.student_repo.fetch_by_course(course_id)
            students = self._calculate_metrics(students)
            
            results = []
            for s in students:
                results.append({
                    "student_id": s.student_id,
                    "name": s.name,
                    "grade": getattr(s, '_temp_grade', 0.0),
                    "attendance": getattr(s, '_temp_attendance', 0)
                })
            return results
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch academic data: {e}")
    
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

    def get_student_metrics_with_cohort(self, student_id: str):
        """
        Get normalized student metrics (0-100 scale) compared to cohort averages.
        Returns data formatted for radar chart visualization.
        """
        try:
            student = self.student_repo.get_by_student_id(student_id)
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch student: {e}")
        
        if not student:
            raise AnalyticsServiceError(f"Student {student_id} not found")
        
        course_code = student.course_code
        
        # Get all students in the same course for cohort calculations
        try:
            cohort_students = self.student_repo.fetch_by_course(course_code)
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch cohort: {e}")
        
        # Calculate metrics for the individual student and cohort
        cohort_students = self._calculate_metrics(cohort_students)
        
        # Find the target student in the calculated metrics
        target_student = next((s for s in cohort_students if s.student_id == student_id), None)
        if not target_student:
            raise AnalyticsServiceError(f"Student {student_id} not found in calculated metrics")
        
        # Get student's recent surveys for stress/sleep averages
        try:
            recent_surveys = self.survey_repo.get_by_student(student_id) if self.survey_repo else []
            completed_surveys = [s for s in recent_surveys if s.status == SurveyStatus.COMPLETED]
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch surveys: {e}")
        
        # Calculate student metrics from most recent survey
        student_stress = 0
        student_sleep = 0
        if completed_surveys:
            # Use the most recent completed survey (they're already ordered chronologically)
            most_recent = completed_surveys[-1]
            student_stress = most_recent.stress if most_recent.stress is not None else 0
            student_sleep = most_recent.sleep if most_recent.sleep is not None else 0
        
        student_grade = getattr(target_student, '_temp_grade', 0.0)
        student_attendance = getattr(target_student, '_temp_attendance', 0)
        
        # Calculate cohort averages
        cohort_grades = [getattr(s, '_temp_grade', 0.0) for s in cohort_students]
        cohort_attendances = [getattr(s, '_temp_attendance', 0) for s in cohort_students]
        
        # Get all cohort surveys for stress/sleep averages
        cohort_stress_values = []
        cohort_sleep_values = []
        for s in cohort_students:
            try:
                surveys = self.survey_repo.get_by_student(s.student_id) if self.survey_repo else []
                completed = [sv for sv in surveys if sv.status == SurveyStatus.COMPLETED]
                cohort_stress_values.extend([sv.stress for sv in completed if sv.stress is not None])
                cohort_sleep_values.extend([sv.sleep for sv in completed if sv.sleep is not None])
            except:
                pass
        
        cohort_stress = sum(cohort_stress_values) / len(cohort_stress_values) if cohort_stress_values else 0
        cohort_sleep = sum(cohort_sleep_values) / len(cohort_sleep_values) if cohort_sleep_values else 0
        cohort_grade = sum(cohort_grades) / len(cohort_grades) if cohort_grades else 0
        cohort_attendance = sum(cohort_attendances) / len(cohort_attendances) if cohort_attendances else 0
        
        # Normalize to 0-100 scale
        def normalize_stress(stress):
            # Direct scaling: higher stress = higher value on chart (more visual impact)
            return (stress / 5) * 100 if stress else 0
        
        def normalize_sleep(sleep):
            # Target 8 hours = 100%, scale proportionally
            return min((sleep / 8) * 100, 100) if sleep else 0
        
        def normalize_attendance(attendance):
            return attendance  # Already in percentage
        
        return {
            'student': {
                'stress': round(normalize_stress(student_stress), 2),
                'sleep': round(normalize_sleep(student_sleep), 2),
                'grades': round(student_grade, 2),
                'attendance': round(normalize_attendance(student_attendance), 2)
            },
            'cohort': {
                'stress': round(normalize_stress(cohort_stress), 2),
                'sleep': round(normalize_sleep(cohort_sleep), 2),
                'grades': round(cohort_grade, 2),
                'attendance': round(normalize_attendance(cohort_attendance), 2)
            }
        }


    def get_officer_snapshot(self):
        """
        Get risk snapshot for all students (Officer View).
        Calculates risk on-demand based on latest data.
        """
        try:
            students = self.student_repo.list()
        except Exception as e:
            raise AnalyticsServiceError(f"Failed to fetch students: {e}")
            
        results = []
        for student in students:
            # Fetch latest survey for metrics
            # Assuming survey_repo is available
            stress = 0
            sleep = 8
            
            if self.survey_repo:
                # This is inefficient (N+1), but acceptable for prototype
                surveys = self.survey_repo.get_by_student(student.student_id)
                if surveys:
                    latest = surveys[-1] # Assuming chronological order
                    stress = latest.stress or 0
                    sleep = latest.sleep or 8
            
            # Prepare metrics
            from src.services.risk_engine import StudentMetricsDTO
            metrics = StudentMetricsDTO(
                stress=stress,
                sleep=sleep,
                misses=student.misses if hasattr(student, 'misses') else student.missed_surveys,
                grade=100.0 # Placeholder for grade
            )
            
            # Calculate risk
            risk_score = self.risk_calculator.compute(metrics)
            
            # Update student record (cache)
            student.current_risk_score = risk_score
            # self.student_repo.update(student) # Optional: persist to DB
            
            results.append({
                "student_id": student.student_id,
                "username": student.name,
                "risk_score": risk_score,
                "stress": stress,
                "sleep": sleep,
                "misses": metrics.misses
            })
            
        return results
