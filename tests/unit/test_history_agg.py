import pytest
from unittest.mock import Mock
from datetime import datetime

from src.services.analytics_service import AnalyticsService, AnalyticsServiceError
from src.dtos.student_history_dto import StudentHistoryDTO
from src.models.survey import SurveyStatus


class TestStudentHistoryAggregation:
    """Test suite for student history aggregation"""
    
    @pytest.fixture
    def mock_risk_calculator(self):
        """Mock RiskCalculator"""
        return Mock()
    
    @pytest.fixture
    def mock_anonymizer(self):
        """Mock Anonymizer"""
        return Mock()
    
    @pytest.fixture
    def mock_student_repo(self):
        """Mock StudentRepository"""
        return Mock()
    
    @pytest.fixture
    def mock_survey_repo(self):
        """Mock SurveyRepository"""
        return Mock()
    
    @pytest.fixture
    def analytics_service(
        self,
        mock_risk_calculator,
        mock_anonymizer,
        mock_student_repo,
        mock_survey_repo
    ):
        """Create AnalyticsService with mocked dependencies"""
        return AnalyticsService(
            risk_calculator=mock_risk_calculator,
            anonymizer=mock_anonymizer,
            student_repo=mock_student_repo,
            survey_repo=mock_survey_repo
        )
    
    def test_get_student_history_returns_chronological_stress_sleep_lists(
        self,
        analytics_service,
        mock_student_repo,
        mock_survey_repo
    ):
        """
        RED TEST: get_student_history returns chronological Stress/Sleep lists
        
        This is the core requirement of Day 4 Dev 4
        """
        # Arrange: Mock student
        mock_student = Mock()
        mock_student.id = 1
        mock_student.student_id = "12345"
        mock_student.name = "Alice Johnson"
        mock_student.email = "alice@example.com"
        mock_student_repo.get_by_student_id.return_value = mock_student
        
        # Mock surveys in chronological order
        mock_survey1 = Mock()
        mock_survey1.week = 10
        mock_survey1.year = 2025
        mock_survey1.stress = 5
        mock_survey1.sleep = 4
        mock_survey1.is_critical = True
        mock_survey1.status = SurveyStatus.COMPLETED
        mock_survey1.created_at = datetime(2025, 3, 10)
        
        mock_survey2 = Mock()
        mock_survey2.week = 11
        mock_survey2.year = 2025
        mock_survey2.stress = 3
        mock_survey2.sleep = 7
        mock_survey2.is_critical = False
        mock_survey2.status = SurveyStatus.COMPLETED
        mock_survey2.created_at = datetime(2025, 3, 17)
        
        mock_survey3 = Mock()
        mock_survey3.week = 12
        mock_survey3.year = 2025
        mock_survey3.stress = 2
        mock_survey3.sleep = 8
        mock_survey3.is_critical = False
        mock_survey3.status = SurveyStatus.COMPLETED
        mock_survey3.created_at = datetime(2025, 3, 24)
        
        # Repository returns surveys in chronological order
        mock_survey_repo.get_by_student.return_value = [
            mock_survey1,
            mock_survey2,
            mock_survey3
        ]
        
        # Act
        result = analytics_service.get_student_history("12345")
        
        # Assert: Returns StudentHistoryDTO
        assert isinstance(result, StudentHistoryDTO)
        
        # Assert: Contains wellbeing history
        assert len(result.wellbeing_history) == 3
        
        # Assert: Chronological order maintained (oldest to newest)
        assert result.wellbeing_history[0].week == 10
        assert result.wellbeing_history[0].stress == 5
        assert result.wellbeing_history[0].sleep == 4
        assert result.wellbeing_history[0].created_at == datetime(2025, 3, 10)
        
        assert result.wellbeing_history[1].week == 11
        assert result.wellbeing_history[1].stress == 3
        assert result.wellbeing_history[1].sleep == 7
        assert result.wellbeing_history[1].created_at == datetime(2025, 3, 17)
        
        assert result.wellbeing_history[2].week == 12
        assert result.wellbeing_history[2].stress == 2
        assert result.wellbeing_history[2].sleep == 8
        assert result.wellbeing_history[2].created_at == datetime(2025, 3, 24)
        
        # Assert: Can extract stress/sleep lists
        stress_list = [record.stress for record in result.wellbeing_history]
        sleep_list = [record.sleep for record in result.wellbeing_history]
        
        assert stress_list == [5, 3, 2]  # Chronological
        assert sleep_list == [4, 7, 8]   # Chronological
    
    def test_get_student_history_returns_dto(
        self,
        analytics_service,
        mock_student_repo,
        mock_survey_repo
    ):
        """Test that get_student_history returns StudentHistoryDTO"""
        # Arrange: Mock student
        mock_student = Mock()
        mock_student.id = 1
        mock_student.student_id = "12345"
        mock_student.name = "Alice Johnson"
        mock_student.email = "alice@example.com"
        mock_student_repo.get_by_student_id.return_value = mock_student
        
        # Mock empty history
        mock_survey_repo.get_by_student.return_value = []
        
        # Act
        result = analytics_service.get_student_history("12345")
        
        # Assert
        assert isinstance(result, StudentHistoryDTO)
        assert result.student_id == "12345"
        assert result.name == "Alice Johnson"
        assert result.email == "alice@example.com"
    
    def test_get_student_history_computes_statistics(
        self,
        analytics_service,
        mock_student_repo,
        mock_survey_repo
    ):
        """Test that statistics are computed correctly"""
        # Arrange
        mock_student = Mock()
        mock_student.id = 1
        mock_student.student_id = "12345"
        mock_student.name = "Alice"
        mock_student.email = "alice@example.com"
        mock_student_repo.get_by_student_id.return_value = mock_student
        
        # 2 completed, 1 skipped survey
        mock_survey1 = Mock()
        mock_survey1.stress = 4
        mock_survey1.sleep = 6
        mock_survey1.status = SurveyStatus.COMPLETED
        mock_survey1.created_at = datetime(2025, 3, 10)
        
        mock_survey2 = Mock()
        mock_survey2.stress = 2
        mock_survey2.sleep = 8
        mock_survey2.status = SurveyStatus.COMPLETED
        mock_survey2.created_at = datetime(2025, 3, 17)
        
        mock_survey3 = Mock()
        mock_survey3.stress = None
        mock_survey3.sleep = None
        mock_survey3.status = SurveyStatus.SKIPPED
        mock_survey3.created_at = datetime(2025, 3, 24)
        
        mock_survey_repo.get_by_student.return_value = [
            mock_survey1,
            mock_survey2,
            mock_survey3
        ]
        
        # Act
        result = analytics_service.get_student_history("12345")
        
        # Assert
        assert result.total_surveys_completed == 2
        assert result.total_surveys_skipped == 1
        assert result.average_stress == 3.0
        assert result.average_sleep == 7.0
    
    def test_get_student_history_raises_error_if_student_not_found(
        self,
        analytics_service,
        mock_student_repo
    ):
        """Test that AnalyticsServiceError is raised if student doesn't exist"""
        # Arrange
        mock_student_repo.get_by_student_id.return_value = None
        
        # Act & Assert
        with pytest.raises(AnalyticsServiceError, match="Student 99999 not found"):
            analytics_service.get_student_history("99999")
    
    def test_get_student_history_handles_none_values_in_surveys(
        self,
        analytics_service,
        mock_student_repo,
        mock_survey_repo
    ):
        """Test that None values in stress/sleep are handled correctly"""
        # Arrange
        mock_student = Mock()
        mock_student.id = 1
        mock_student.student_id = "12345"
        mock_student.name = "Alice"
        mock_student.email = "alice@example.com"
        mock_student_repo.get_by_student_id.return_value = mock_student
        
        # Survey with None values
        mock_survey = Mock()
        mock_survey.week = 10
        mock_survey.year = 2025
        mock_survey.stress = None
        mock_survey.sleep = None
        mock_survey.status = SurveyStatus.COMPLETED
        mock_survey.is_critical = False
        mock_survey.created_at = datetime(2025, 3, 10)
        
        mock_survey_repo.get_by_student.return_value = [mock_survey]
        
        # Act
        result = analytics_service.get_student_history("12345")
        
        # Assert - averages should be None when all values are None
        assert result.average_stress is None
        assert result.average_sleep is None