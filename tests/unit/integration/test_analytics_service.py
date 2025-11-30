import pytest
from src.services.analytics_service import AnalyticsService


class FakeRiskCalculator:
    def calculate(self, students):
        return [{"x": 70, "y": 50, "r": 0.82}]  # dummy correlation output


class FakeAnonymizer:
    def anonymize(self, students):
        # Proper anonymization removes sensitive fields
        return [
            {
                "score": s["score"],
                "attendance": s["attendance"],
                "student_id": None,  # enforced null here
                "name": None,
                "email": None,
            }
            for s in students
        ]


class FakeStudentRepository:
    def fetch_all(self):
        return [
            {
                "student_id": "S123",
                "name": "Alice",
                "email": "alice@Warwick.ac.uk",
                "score": 78,
                "attendance": 0.8,
            }
        ]


@pytest.mark.integration
def test_director_privacy_enforcement():
    repo = FakeStudentRepository()
    anonymizer = FakeAnonymizer()
    rc = FakeRiskCalculator()

    svc = AnalyticsService(
        risk_calculator=rc,
        anonymizer=anonymizer,
        student_repo=repo,
    )

    # --- CALL WITH EXCEPTION HANDLING ---
    try:
        result = svc.get_correlations_for_director()
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
    assert "x" in result[0], "Metric 'x' missing"
    assert "y" in result[0], "Metric 'y' missing"
    assert "r" in result[0], "Metric 'r' missing"
