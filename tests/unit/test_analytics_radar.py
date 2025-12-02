import pytest
from unittest.mock import Mock, MagicMock
from src.services.analytics_service import AnalyticsService, AnalyticsServiceError
from src.models.student import Student
from src.models.survey import WellbeingSurvey, SurveyStatus
from datetime import datetime

class TestAnalyticsRadar:
    @pytest.fixture
    def mock_student_repo(self):
        return Mock()

    @pytest.fixture
    def mock_survey_repo(self):
        return Mock()

    @pytest.fixture
    def mock_risk_calculator(self):
        return Mock()

    @pytest.fixture
    def mock_anonymizer(self):
        return Mock()

    @pytest.fixture
    def analytics_service(self, mock_student_repo, mock_survey_repo, mock_risk_calculator, mock_anonymizer):
        service = AnalyticsService(
            risk_calculator=mock_risk_calculator,
            anonymizer=mock_anonymizer,
            student_repo=mock_student_repo,
            survey_repo=mock_survey_repo
        )
        
        # Mock _calculate_metrics to avoid DB calls
        def mock_calc(students):
            for s in students:
                if s.student_id == "student1":
                    s._temp_grade = 75.0
                    s._temp_attendance = 90.0
                else:
                    s._temp_grade = 80.0
                    s._temp_attendance = 95.0
            return students
            
        service._calculate_metrics = Mock(side_effect=mock_calc)
        return service

    def test_get_student_metrics_success(self, analytics_service, mock_student_repo, mock_survey_repo):
        # Setup student
        student = Student(student_id="student1", name="Test Student", email="test@test.com", course_code="CS101")
        student._temp_grade = 75.0
        student._temp_attendance = 90.0
        mock_student_repo.get_by_student_id.return_value = student
        
        # Setup cohort
        cohort_student = Student(student_id="student2", name="Cohort Student", email="cohort@test.com", course_code="CS101")
        cohort_student._temp_grade = 80.0
        cohort_student._temp_attendance = 95.0
        mock_student_repo.fetch_by_course.return_value = [student, cohort_student]
        
        # Setup surveys
        survey1 = WellbeingSurvey(student_id="student1", stress=3, sleep=7, week=1, year=2023)
        survey1.status = SurveyStatus.COMPLETED
        mock_survey_repo.get_by_student.side_effect = lambda sid: [survey1] if sid == "student1" else []
        
        # Execute
        result = analytics_service.get_student_metrics_with_cohort("student1")
        
        # Verify
        assert result['student']['grades'] == 75.0
        assert result['student']['attendance'] == 90.0
        assert result['student']['stress'] == 60.0  # (3/5)*100
        assert result['student']['sleep'] == 87.5   # (7/8)*100
        
        assert 'cohort' in result
        assert result['cohort']['grades'] == 77.5
        assert result['cohort']['attendance'] == 92.5

    def test_get_student_metrics_student_not_found(self, analytics_service, mock_student_repo):
        mock_student_repo.get_by_student_id.return_value = None
        
        with pytest.raises(AnalyticsServiceError, match="Student non_existent not found"):
            analytics_service.get_student_metrics_with_cohort("non_existent")

    def test_get_student_metrics_repo_error(self, analytics_service, mock_student_repo):
        mock_student_repo.get_by_student_id.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch student"):
            analytics_service.get_student_metrics_with_cohort("student1")

    def test_get_student_metrics_cohort_error(self, analytics_service, mock_student_repo):
        student = Student(student_id="student1", name="Test", email="test@test.com", course_code="CS101")
        mock_student_repo.get_by_student_id.return_value = student
        mock_student_repo.fetch_by_course.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch cohort"):
            analytics_service.get_student_metrics_with_cohort("student1")

    def test_get_student_metrics_survey_error(self, analytics_service, mock_student_repo, mock_survey_repo):
        student = Student(student_id="student1", name="Test", email="test@test.com", course_code="CS101")
        mock_student_repo.get_by_student_id.return_value = student
        mock_student_repo.fetch_by_course.return_value = [student]
        mock_survey_repo.get_by_student.side_effect = Exception("DB Error")
        
        with pytest.raises(AnalyticsServiceError, match="Failed to fetch surveys"):
            analytics_service.get_student_metrics_with_cohort("student1")

    def test_get_student_metrics_cohort_survey_error(self, analytics_service, mock_student_repo, mock_survey_repo):
        student = Student(student_id="student1", name="Test", email="test@test.com", course_code="CS101")
        cohort_student = Student(student_id="student2", name="Cohort", email="cohort@test.com", course_code="CS101")
        
        mock_student_repo.get_by_student_id.return_value = student
        mock_student_repo.fetch_by_course.return_value = [student, cohort_student]
        
        # Mock survey repo to raise exception for cohort student
        def mock_get_surveys(sid):
            if sid == "student2":
                raise Exception("DB Error")
            return []
            
        mock_survey_repo.get_by_student.side_effect = mock_get_surveys
        
        # Execute - should not raise exception, just skip that student's surveys
        result = analytics_service.get_student_metrics_with_cohort("student1")
        
        assert result['cohort']['stress'] == 0
        assert result['cohort']['sleep'] == 0

    def test_get_student_metrics_no_surveys(self, analytics_service, mock_student_repo, mock_survey_repo):
        student = Student(student_id="student1", name="Test", email="test@test.com", course_code="CS101")
        mock_student_repo.get_by_student_id.return_value = student
        mock_student_repo.fetch_by_course.return_value = [student]
        mock_survey_repo.get_by_student.return_value = []
        
        result = analytics_service.get_student_metrics_with_cohort("student1")
        
        assert result['student']['stress'] == 0
        assert result['student']['sleep'] == 0

    def test_get_student_metrics_student_not_in_cohort(self, analytics_service, mock_student_repo):
        student = Student(student_id="student1", name="Test", email="test@test.com", course_code="CS101")
        mock_student_repo.get_by_student_id.return_value = student
        # Return empty list or list without the student
        mock_student_repo.fetch_by_course.return_value = []
        
        with pytest.raises(AnalyticsServiceError, match="Student student1 not found in calculated metrics"):
            analytics_service.get_student_metrics_with_cohort("student1")
