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

    def test_get_director_risk_view_fetch_error(self, service, mock_student_repo):
        mock_student_repo.fetch_by_course.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch student data"):
            service.get_director_risk_view("course1")

    def test_get_director_risk_view_anonymize_error(self, service, mock_student_repo, mock_anonymizer):
        mock_student_repo.fetch_by_course.return_value = []
        mock_anonymizer.anonymize.side_effect = Exception("Anon Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to anonymize data"):
            service.get_director_risk_view("course1")

    def test_get_director_risk_view_risk_calc_error(self, service, mock_student_repo, mock_anonymizer, mock_risk_calculator):
        mock_student_repo.fetch_by_course.return_value = []
        mock_anonymizer.anonymize.return_value = []
        mock_risk_calculator.calculate.side_effect = Exception("Risk Error")
        
        with pytest.raises(AnalyticsServiceError, match="Risk calculation failed"):
            service.get_director_risk_view("course1")

    def test_get_director_academic_view_fetch_error(self, service, mock_student_repo):
        mock_student_repo.fetch_by_course.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch academic data"):
            service.get_director_academic_view("course1")
            
    def test_get_director_academic_view_success(self, service, mock_student_repo):
        student = MagicMock()
        student.student_id = "s1"
        student.name = "Test Student"
        student.id = 1
        mock_student_repo.fetch_by_course.return_value = [student]
        
        # Mock session query for grades/attendance
        mock_session = MagicMock()
        mock_student_repo.session = mock_session
        mock_session.query.return_value.filter_by.return_value.all.return_value = []
        
        results = service.get_director_academic_view("course1")
        assert len(results) == 1
        assert results[0]['name'] == "Test Student"
        assert results[0]['grade'] == 0.0
        assert results[0]['attendance'] == 0

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

    def test_get_director_risk_view_success(self, service, mock_student_repo, mock_anonymizer, mock_risk_calculator):
        student = MagicMock()
        student.id = 1
        mock_student_repo.fetch_by_course.return_value = [student]
        
        # Mock session query for grades/attendance
        mock_session = MagicMock()
        mock_student_repo.session = mock_session
        grade = MagicMock()
        grade.grade = 80.0
        attendance = MagicMock()
        attendance.status = 'Present'
        
        # Configure side_effect for query().filter_by().all()
        # First call: grades, Second call: attendance
        mock_session.query.return_value.filter_by.return_value.all.side_effect = [[grade], [attendance]]
        
        mock_anonymizer.anonymize.return_value = [{"name": "Test", "email": "t@t.com", "student_id": "s1"}]
        mock_risk_calculator.calculate.return_value = [{"risk_score": 10}]
        
        results = service.get_director_risk_view("course1")
        
        assert len(results) == 1
        # Verify shuffling (hard to test deterministically, but we can check it returns a list)
        assert isinstance(results, list)
        
    def test_get_student_history_success(self, service, mock_student_repo, mock_survey_repo):
        student = MagicMock()
        student.student_id = "s1"
        student.name = "Test"
        student.email = "t@t.com"
        mock_student_repo.get_by_student_id.return_value = student
        
        from src.models.survey import SurveyStatus
        survey1 = MagicMock(week=1, year=2023, stress=5, sleep=7, is_critical=False, status=SurveyStatus.COMPLETED, created_at="date")
        survey2 = MagicMock(week=2, year=2023, stress=None, sleep=None, is_critical=False, status=SurveyStatus.SKIPPED, created_at="date")
        mock_survey_repo.get_by_student.return_value = [survey1, survey2]
        
        dto = service.get_student_history("s1")
        
        assert dto.student_id == "s1"
        assert dto.total_surveys_completed == 1
        assert dto.total_surveys_skipped == 1
        assert dto.average_stress == 5.0
        assert dto.average_sleep == 7.0
        
    def test_get_officer_snapshot_success(self, service, mock_student_repo, mock_survey_repo, mock_risk_calculator):
        student = MagicMock()
        student.student_id = "s1"
        student.name = "Test"
        student.misses = 1
        mock_student_repo.list.return_value = [student]
        
        survey = MagicMock(stress=5, sleep=7)
        mock_survey_repo.get_by_student.return_value = [survey]
        
        mock_risk_calculator.compute.return_value = 50.0
        
        results = service.get_officer_snapshot()
        
        assert len(results) == 1
        assert results[0]['student_id'] == "s1"
        assert results[0]['risk_score'] == 50.0
        assert results[0]['stress'] == 5
        assert results[0]['sleep'] == 7
        
    def test_get_officer_snapshot_no_surveys(self, service, mock_student_repo, mock_survey_repo, mock_risk_calculator):
        student = MagicMock()
        student.student_id = "s1"
        student.misses = 0
        mock_student_repo.list.return_value = [student]
        mock_survey_repo.get_by_student.return_value = []
        
        mock_risk_calculator.compute.return_value = 10.0
        
        results = service.get_officer_snapshot()
        
        assert len(results) == 1
        assert results[0]['stress'] == 0
        assert results[0]['sleep'] == 8

    def test_get_officer_snapshot_fetch_error(self, service, mock_student_repo):
        mock_student_repo.list.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch students"):
            service.get_officer_snapshot()
