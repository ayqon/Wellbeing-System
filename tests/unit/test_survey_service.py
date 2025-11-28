import pytest
from unittest.mock import Mock
from src.services.survey_service import SurveyService
from src.models.survey import SurveyStatus


class TestSurveyService:
    """Test suite for SurveyService"""

    def test_survey_service_initialization(self):
        """Test SurveyService can be initialized"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        assert service is not None

    def test_process_skip_creates_skipped_survey(self):
        """Test process_skip creates SKIPPED survey when none exists"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        # No existing survey
        mock_survey_repo.get_by_student_week.return_value = None
        
        fake_student = Mock()
        fake_student.increment_misses = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        service.process_skip(student_id="12345", week=10, year=2025)
        
        # Should create survey
        mock_survey_repo.create.assert_called_once()
        fake_student.increment_misses.assert_called_once()

    def test_process_skip_raises_error_if_survey_exists(self):
        """Test process_skip raises error when survey already exists (any status)"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        # Existing survey (any status)
        fake_survey = Mock()
        mock_survey_repo.get_by_student_week.return_value = fake_survey
        
        mock_student_repo.get_by_student_id.return_value = Mock()
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        # Should raise error
        with pytest.raises(ValueError, match="Survey already exists"):
            service.process_skip(student_id="12345", week=10, year=2025)

    def test_process_skip_with_different_student_ids(self):
        """Test process_skip works with different student IDs"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        mock_survey_repo.get_by_student_week.return_value = None
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        # Test with different IDs
        service.process_skip(student_id="W12345", week=10, year=2025)
        mock_student_repo.get_by_student_id.assert_called_with("W12345")

    def test_process_skip_handles_student_not_found(self):
        """Test process_skip raises error when student doesn't exist"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        mock_student_repo.get_by_student_id.return_value = None
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Student 12345 not found"):
            service.process_skip(student_id="12345", week=10, year=2025)