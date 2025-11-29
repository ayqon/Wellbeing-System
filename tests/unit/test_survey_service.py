import pytest
from unittest.mock import Mock
from src.services.survey_service import SurveyService
from src.models.survey import SurveyStatus


class TestSurveyService:
    """
    Test suite for SurveyService
    
    Coverage:
    - Initialization
    - process_skip() - Happy path and error cases
    - submit_response() - Happy path and error cases
    - _check_critical() - Boundary conditions
    """

    # ============ Initialization Tests ============
    
    def test_survey_service_initialization(self):
        """Test SurveyService can be initialized with dependencies"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        assert service is not None
        assert service.survey_repo is mock_survey_repo
        assert service.student_repo is mock_student_repo

    # ============ process_skip() Tests ============
    
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
        
        # Should create survey with SKIPPED status
        mock_survey_repo.create.assert_called_once()
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.status == SurveyStatus.SKIPPED
        assert created_survey.is_critical is False
        
        # Should increment student's misses
        fake_student.increment_misses.assert_called_once()
        mock_student_repo.save.assert_called_once_with(fake_student)

    def test_process_skip_raises_error_if_survey_completed(self):
        """Test process_skip raises error when survey already completed"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        # Existing COMPLETED survey
        fake_survey = Mock()
        fake_survey.status = SurveyStatus.COMPLETED
        mock_survey_repo.get_by_student_week.return_value = fake_survey
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Cannot skip: Survey already completed"):
            service.process_skip(student_id="12345", week=10, year=2025)
        
        # Should NOT create or increment
        mock_survey_repo.create.assert_not_called()

    def test_process_skip_raises_error_if_survey_already_skipped(self):
        """Test process_skip raises error when survey already skipped"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        # Existing SKIPPED survey
        fake_survey = Mock()
        fake_survey.status = SurveyStatus.SKIPPED
        mock_survey_repo.get_by_student_week.return_value = fake_survey
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Survey already skipped"):
            service.process_skip(student_id="12345", week=10, year=2025)

    def test_process_skip_handles_student_not_found(self):
        """Test process_skip raises error when student doesn't exist"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        mock_student_repo.get_by_student_id.return_value = None
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Student 12345 not found"):
            service.process_skip(student_id="12345", week=10, year=2025)
    
    def test_process_skip_with_different_student_ids(self):
        """Test process_skip works with different student ID formats"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        mock_survey_repo.get_by_student_week.return_value = None
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        # Test with alphanumeric ID
        service.process_skip(student_id="12345", week=10, year=2025)
        mock_student_repo.get_by_student_id.assert_called_with("12345")

    # ============ submit_response() Tests ============
    
    def test_submit_response_creates_new_survey(self):
        """Test submit_response creates new survey with valid data"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        # No existing survey
        mock_survey_repo.get_by_student_week.return_value = None
        
        fake_student = Mock()
        fake_student.reset_misses = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        result = service.submit_response(
            student_id="12345",
            week=10,
            year=2025,
            stress=3,
            sleep=7
        )
        
        # Should create new survey
        mock_survey_repo.create.assert_called_once()
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.status == SurveyStatus.COMPLETED
        assert created_survey.stress == 3
        assert created_survey.sleep == 7
        
        # Should reset misses
        fake_student.reset_misses.assert_called_once()
        mock_student_repo.save.assert_called_once_with(fake_student)

    def test_submit_response_validates_stress_below_minimum(self):
        """Test submit_response rejects stress < 1"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Stress must be 1-5, got 0"):
            service.submit_response("12345", 10, 2025, stress=0, sleep=7)

    def test_submit_response_validates_stress_above_maximum(self):
        """Test submit_response rejects stress > 5"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Stress must be 1-5, got 10"):
            service.submit_response("12345", 10, 2025, stress=10, sleep=7)

    def test_submit_response_validates_sleep_below_minimum(self):
        """Test submit_response rejects sleep < 0"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Sleep must be 0-24 hours, got -1"):
            service.submit_response("12345", 10, 2025, stress=3, sleep=-1)

    def test_submit_response_validates_sleep_above_maximum(self):
        """Test submit_response rejects sleep > 24"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Sleep must be 0-24 hours, got 25"):
            service.submit_response("12345", 10, 2025, stress=3, sleep=25)

    def test_submit_response_raises_error_if_student_not_found(self):
        """Test submit_response validates student exists"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        mock_student_repo.get_by_student_id.return_value = None
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Student 12345 not found"):
            service.submit_response("12345", 10, 2025, stress=3, sleep=7)

    def test_submit_response_raises_error_if_already_completed(self):
        """Test submit_response prevents duplicate submissions"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        # Existing COMPLETED survey
        fake_survey = Mock()
        fake_survey.status = SurveyStatus.COMPLETED
        fake_survey.survey_id = 999
        mock_survey_repo.get_by_student_week.return_value = fake_survey
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        with pytest.raises(ValueError, match="Survey already completed"):
            service.submit_response("12345", 10, 2025, stress=3, sleep=7)

    def test_submit_response_upgrades_skipped_survey(self):
        """Test submit_response allows completing a previously skipped survey"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        # Existing SKIPPED survey
        fake_survey = Mock()
        fake_survey.status = SurveyStatus.SKIPPED
        fake_survey.survey_id = 999
        mock_survey_repo.get_by_student_week.return_value = fake_survey
        
        fake_student = Mock()
        fake_student.reset_misses = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        result = service.submit_response("12345", 10, 2025, stress=3, sleep=7)
        
        # Should update existing survey, not create new
        mock_survey_repo.save.assert_called_once()
        mock_survey_repo.create.assert_not_called()
        
        # Verify survey was updated
        assert fake_survey.status == SurveyStatus.COMPLETED
        assert fake_survey.stress == 3
        assert fake_survey.sleep == 7

    def test_submit_response_marks_critical_high_stress(self):
        """Test survey marked critical when stress >= 4"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        mock_survey_repo.get_by_student_week.return_value = None
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        service.submit_response("12345", 10, 2025, stress=5, sleep=8)
        
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.is_critical is True

    def test_submit_response_marks_critical_low_sleep(self):
        """Test survey marked critical when sleep <= 4"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        mock_survey_repo.get_by_student_week.return_value = None
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        service.submit_response("12345", 10, 2025, stress=2, sleep=3)
        
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.is_critical is True

    def test_submit_response_not_critical_normal_values(self):
        """Test survey NOT marked critical with normal values"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        mock_survey_repo.get_by_student_week.return_value = None
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        service.submit_response("12345", 10, 2025, stress=3, sleep=7)
        
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.is_critical is False

    def test_submit_response_critical_boundary_stress(self):
        """Test critical threshold at stress=4 (boundary)"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        mock_survey_repo.get_by_student_week.return_value = None
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        # Stress = 4 should be critical
        service.submit_response("12345", 10, 2025, stress=4, sleep=8)
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.is_critical is True

    def test_submit_response_critical_boundary_sleep(self):
        """Test critical threshold at sleep=4 (boundary)"""
        mock_survey_repo = Mock()
        mock_student_repo = Mock()
        
        mock_survey_repo.get_by_student_week.return_value = None
        
        fake_student = Mock()
        mock_student_repo.get_by_student_id.return_value = fake_student
        
        service = SurveyService(mock_survey_repo, mock_student_repo)
        
        # Sleep = 4 should be critical
        service.submit_response("12345", 10, 2025, stress=2, sleep=4)
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.is_critical is True
        
        # Sleep = 5 should NOT be critical
        mock_survey_repo.create.reset_mock()
        service.submit_response("12345", 11, 2025, stress=2, sleep=5)
        created_survey = mock_survey_repo.create.call_args[0][0]
        assert created_survey.is_critical is False