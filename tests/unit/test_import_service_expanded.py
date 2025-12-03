import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import io
from src.services.import_service import ImportService
from src.models.academic import ModuleGrade, AttendanceRegister, Module
from src.models.student import Student
from src.models.survey import WellbeingSurvey, SurveyStatus

class TestImportServiceExpanded:
    @pytest.fixture
    def mock_user_repo(self):
        repo = MagicMock()
        repo.session = MagicMock()
        return repo

    @pytest.fixture
    def mock_student_repo(self):
        return MagicMock()

    @pytest.fixture
    def mock_parser(self):
        return MagicMock()

    @pytest.fixture
    def service(self, mock_user_repo, mock_student_repo, mock_parser):
        return ImportService(mock_user_repo, mock_student_repo, mock_parser)

    def test_process_grade_csv_success(self, service):
        # Setup
        csv_content = "student_id,module_code,grade\nS1,M1,85"
        stream = io.StringIO(csv_content)
        
        # Mocks
        student = Student(student_id="S1", name="Test", email="t@t.com")
        student.id = 1
        service.student_repo.get_by_student_id.return_value = student
        
        module = Module(module_code="M1", name="Mod", course=None)
        module.id = 10
        service.db_session.query.return_value.filter_by.return_value.first.return_value = module
        
        # Execute
        result = service.process_grade_csv(stream)
        
        # Verify
        assert result['success'] == 1
        assert result['errors'] == 0
        service.db_session.add.assert_called()
        service.db_session.commit.assert_called()

    def test_process_attendance_csv_success(self, service):
        # Setup
        csv_content = "student_id,module_code,date,status\nS1,M1,2025-10-01,Present"
        stream = io.StringIO(csv_content)
        
        # Mocks
        student = Student(student_id="S1", name="Test", email="t@t.com")
        student.id = 1
        service.student_repo.get_by_student_id.return_value = student
        
        module = Module(module_code="M1", name="Mod", course=None)
        module.id = 10
        service.db_session.query.return_value.filter_by.return_value.first.return_value = module
        
        # Execute
        result = service.process_attendance_csv(stream)
        
        # Verify
        assert result['success'] == 1
        assert result['errors'] == 0
        service.db_session.add.assert_called()
        args, _ = service.db_session.add.call_args
        assert isinstance(args[0], AttendanceRegister)
        assert args[0].status == "Present"

    def test_process_survey_csv_success(self, service):
        # Setup
        csv_content = "student_id,week,stress,sleep\nS1,5,3,7.5"
        stream = io.StringIO(csv_content)
        
        # Mocks
        student = Student(student_id="S1", name="Test", email="t@t.com")
        service.student_repo.get_by_student_id.return_value = student
        
        # Execute
        result = service.process_survey_csv(stream)
        
        # Verify
        assert result['success'] == 1
        assert result['errors'] == 0
        service.db_session.add.assert_called()
        args, _ = service.db_session.add.call_args
        assert isinstance(args[0], WellbeingSurvey)
        assert args[0].stress == 3
        assert args[0].sleep == 7.5
        assert not args[0].is_critical

    def test_process_survey_csv_critical(self, service):
        # Setup - High stress
        csv_content = "student_id,week,stress,sleep\nS1,5,5,7.5"
        stream = io.StringIO(csv_content)
        
        student = Student(student_id="S1", name="Test", email="t@t.com")
        service.student_repo.get_by_student_id.return_value = student
        
        result = service.process_survey_csv(stream)
        
        args, _ = service.db_session.add.call_args
        assert args[0].is_critical is True

    def test_process_grade_csv_row_error(self, service):
        # Setup - Valid CSV, but repo raises exception
        csv_content = "student_id,module_code,grade\nS1,M1,85"
        stream = io.StringIO(csv_content)
        
        # Mock student lookup to fail
        service.student_repo.get_by_student_id.side_effect = Exception("Lookup Error")
        
        result = service.process_grade_csv(stream)
        
        assert result['errors'] == 1
        assert "Row error" in result['details'][0]

    def test_process_grade_csv_rollback(self, service):
        csv_content = "student_id,module_code,grade\nS1,M1,85"
        stream = io.StringIO(csv_content)
        
        service.student_repo.get_by_student_id.return_value = MagicMock()
        service.db_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        service.db_session.commit.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception, match="DB Error"):
            service.process_grade_csv(stream)
        
        service.db_session.rollback.assert_called()

    def test_process_attendance_csv_row_error(self, service):
        csv_content = "student_id,module_code,date,status\nS1,M1,invalid-date,Present"
        stream = io.StringIO(csv_content)
        
        service.student_repo.get_by_student_id.return_value = MagicMock()
        service.db_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        result = service.process_attendance_csv(stream)
        
        assert result['errors'] == 1
        assert "Row error" in result['details'][0]

    def test_process_attendance_csv_rollback(self, service):
        csv_content = "student_id,module_code,date,status\nS1,M1,2023-01-01,Present"
        stream = io.StringIO(csv_content)
        
        service.student_repo.get_by_student_id.return_value = MagicMock()
        service.db_session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        service.db_session.commit.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception, match="DB Error"):
            service.process_attendance_csv(stream)
            
        service.db_session.rollback.assert_called()

    def test_process_survey_csv_row_error(self, service):
        # Setup - Valid CSV, but repo raises exception
        csv_content = "student_id,week,stress,sleep\nS1,5,3,7.5"
        stream = io.StringIO(csv_content)
        
        service.student_repo.get_by_student_id.side_effect = Exception("Lookup Error")
        
        result = service.process_survey_csv(stream)
        
        assert result['errors'] == 1
        assert "Row error" in result['details'][0]

    def test_process_survey_csv_rollback(self, service):
        csv_content = "student_id,week,stress,sleep\nS1,5,3,7.5"
        stream = io.StringIO(csv_content)
        
        service.student_repo.get_by_student_id.return_value = MagicMock()
        service.db_session.commit.side_effect = Exception("DB Error")
        
        with pytest.raises(Exception, match="DB Error"):
            service.process_survey_csv(stream)
            
        service.db_session.rollback.assert_called()
