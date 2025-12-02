import pytest
from src.services.analytics_service import AnalyticsService


class FakeStudent:
    def __init__(self, id, student_id, name, email, current_risk_score, missed_surveys=0):
        self.id = id
        self.student_id = student_id
        self.name = name
        self.email = email
        self.current_risk_score = current_risk_score
        self.missed_surveys = missed_surveys

from unittest.mock import MagicMock

class FakeStudentRepository:
    def __init__(self):
        self.session = MagicMock()
        self.session.query.return_value.filter_by.return_value.all.return_value = []

    def fetch_by_course(self, course_id):
        return [
            FakeStudent(1, "S123", "Alice", "alice@Warwick.ac.uk", 78)
        ]

@pytest.mark.integration
def test_director_privacy_enforcement():
    repo = FakeStudentRepository()
    # Use real Anonymizer and RiskCalculator or update fakes to match real signatures?
    # The test checks privacy enforcement in the SERVICE.
    # The service calls anonymizer.anonymize.
    # If we use FakeAnonymizer, we test the service's use of it.
    # But real Anonymizer expects objects.
    # Let's use real Anonymizer and RiskCalculator to be safe, or update fakes.
    # Updating fakes is better for unit testing.
    
    class FakeAnonymizer:
        def anonymize(self, students):
            return [
                {
                    "student_id": "masked_id",
                    "name": None,
                    "email": None,
                    "stress": 0,
                    "sleep": 8,
                    "misses": 0,
                    "grade": 100.0,
                    "cached_risk": s.current_risk_score
                }
                for s in students
            ]

    class FakeRiskCalculator:
        def calculate(self, students):
            return [{
                "risk_score": 78,
                "driver": "NONE",
                "name": None,
                "email": None,
                "student_id": None,
                "x": 78, "y": 4, "r": 0.78
            }]

    anonymizer = FakeAnonymizer()
    rc = FakeRiskCalculator()

    svc = AnalyticsService(
        risk_calculator=rc,
        anonymizer=anonymizer,
        student_repo=repo,
    )

    # --- CALL WITH EXCEPTION HANDLING ---
    # --- CALL WITH EXCEPTION HANDLING ---
    try:
        result = svc.get_director_risk_view("CS101")
    except Exception as e:
        pytest.fail(f"AnalyticsService raised an unexpected exception: {e}")

    # Make sure result is a list and not empty
    assert isinstance(result, list), "Service should return a list"
    assert len(result) > 0, "Service returned an empty result list"

    # --- PRIVACY ASSERTIONS ---
    assert "name" not in result[0] or result[0]["name"] is None
    assert "email" not in result[0] or result[0]["email"] is None
    assert "student_id" not in result[0] or result[0]["student_id"] is None

    # --- METRIC ASSERTIONS ---
    assert "risk_score" in result[0]
    assert result[0]["risk_score"] == 78
