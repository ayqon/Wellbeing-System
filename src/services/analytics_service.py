class AnalyticsServiceError(Exception):
    """Base class for analytics-related errors."""
    pass


class AnalyticsService:
    ###* **DI:** Inject `RiskCalculator`, `Anonymizer`, and `StudentRepository`.
    def __init__(self, risk_calculator, anonymizer, student_repo): 
        self.risk_calculator = risk_calculator
        self.anonymizer = anonymizer
        self.student_repo = student_repo

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

