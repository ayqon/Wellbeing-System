import pytest
from unittest.mock import MagicMock
from src.services.analytics_service import AnalyticsService, AnalyticsServiceError

class TestAnalyticsService:
    @pytest.fixture
    def mock_risk_calculator(self):
        return MagicMock()

    @pytest.fixture
    def mock_anonymizer(self):
        return MagicMock()

    @pytest.fixture
    def mock_student_repo(self):
        return MagicMock()

    @pytest.fixture
    def mock_survey_repo(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_risk_calculator, mock_anonymizer, mock_student_repo, mock_survey_repo):
        return AnalyticsService(mock_risk_calculator, mock_anonymizer, mock_student_repo, mock_survey_repo)

    def test_get_director_view_fetch_error(self, service, mock_student_repo):
        mock_student_repo.fetch_by_course.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch student data"):
            service.get_director_view("course1")

    def test_get_director_view_anonymize_error(self, service, mock_student_repo, mock_anonymizer):
        mock_student_repo.fetch_by_course.return_value = []
        mock_anonymizer.anonymize.side_effect = Exception("Anon Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to anonymize data"):
            service.get_director_view("course1")

    def test_get_director_view_risk_calc_error(self, service, mock_student_repo, mock_anonymizer, mock_risk_calculator):
        mock_student_repo.fetch_by_course.return_value = []
        mock_anonymizer.anonymize.return_value = []
        mock_risk_calculator.calculate.side_effect = Exception("Risk Error")
        
        with pytest.raises(AnalyticsServiceError, match="Risk calculation failed"):
            service.get_director_view("course1")

    def test_get_student_history_fetch_student_error(self, service, mock_student_repo):
        mock_student_repo.get_by_student_id.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch student"):
            service.get_student_history("s1")

    def test_get_student_history_student_not_found(self, service, mock_student_repo):
        mock_student_repo.get_by_student_id.return_value = None
        
        with pytest.raises(AnalyticsServiceError, match="Student s1 not found"):
            service.get_student_history("s1")

    def test_get_student_history_fetch_surveys_error(self, service, mock_student_repo, mock_survey_repo):
        mock_student_repo.get_by_student_id.return_value = MagicMock()
        mock_survey_repo.get_by_student.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch surveys"):
            service.get_student_history("s1")

    def test_get_officer_snapshot_fetch_error(self, service, mock_student_repo):
        mock_student_repo.list.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch students"):
            service.get_officer_snapshot()
