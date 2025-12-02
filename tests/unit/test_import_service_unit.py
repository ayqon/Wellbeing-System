import pytest
from unittest.mock import MagicMock, Mock
import io
from src.services.import_service import ImportService

class TestImportService:
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

    def test_execute_import_detects_user_csv(self, service):
        service.process_user_csv = MagicMock()
        file_stream = io.BytesIO(b"username,password\n")
        
        service.execute_import(file_stream)
        service.process_user_csv.assert_called_once()

    def test_execute_import_detects_academic_csv(self, service):
        service.process_academic_csv = MagicMock()
        file_stream = io.BytesIO(b"student_id,module_code\n")
        
        service.execute_import(file_stream)
        service.process_academic_csv.assert_called_once()

    def test_process_user_csv_success(self, service, mock_parser, mock_user_repo, mock_student_repo):
        mock_parser.parse.return_value = [{
            'username': 'u1', 'password_hash': 'p1', 'role': 'STUDENT',
            'student_id': 's1', 'name': 'n1', 'email': 'e1'
        }]
        file_stream = MagicMock()
        
        result = service.process_user_csv(file_stream)
        
        assert result['success'] == 1
        assert result['errors'] == 0
        mock_user_repo.add.assert_called()
        mock_student_repo.add.assert_called()
        mock_user_repo.session.commit.assert_called()

    def test_process_user_csv_row_error(self, service, mock_parser, mock_user_repo):
        mock_parser.parse.return_value = [{'username': 'u1'}] # Missing keys will cause KeyError
        file_stream = MagicMock()
        
        # Mock User creation to fail or let it fail naturally
        # The service code accesses row['password_hash'] which will raise KeyError
        
        result = service.process_user_csv(file_stream)
        
        assert result['success'] == 0
        assert result['errors'] == 1
        mock_user_repo.session.rollback.assert_called() # Row rollback
        mock_user_repo.session.commit.assert_called() # Final commit (even if 0 success, it commits the session state)

    def test_process_academic_csv_success_grade(self, service, mock_student_repo, mock_user_repo):
        csv_content = "student_id,module_code,type,value,date\nS1,M1,grade,80,2023-01-01"
        file_stream = io.StringIO(csv_content)
        
        mock_student = MagicMock()
        mock_student.id = 1
        mock_student_repo.get_by_student_id.return_value = mock_student
        
        mock_module = MagicMock()
        mock_module.id = 1
        # Mocking session.query(...).filter_by(...).first()
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = mock_module
        
        result = service.process_academic_csv(file_stream)
        
        assert result['success'] == 1
        mock_user_repo.session.add.assert_called() # Adds grade
        mock_user_repo.session.commit.assert_called()

    def test_process_academic_csv_unknown_type(self, service, mock_student_repo, mock_user_repo):
        csv_content = "student_id,module_code,type,value,date\nS1,M1,unknown,80,2023-01-01"
        file_stream = io.StringIO(csv_content)
        
        mock_student_repo.get_by_student_id.return_value = MagicMock()
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        result = service.process_academic_csv(file_stream)
        
        assert result['errors'] == 1
        assert "Unknown type" in result['details'][0]

    def test_execute_import_fallback(self, service):
        service.process_user_csv = MagicMock()
        # Stream without seek/read or just empty that doesn't match headers
        file_stream = MagicMock()
        del file_stream.read 
        
        service.execute_import(file_stream)
        service.process_user_csv.assert_called_once()

    def test_process_user_csv_bytes_input(self, service, mock_parser, mock_user_repo, mock_student_repo):
        mock_parser.parse.return_value = []
        file_stream = b"username,password"
        
        service.process_user_csv(file_stream)
        
        # Verify parser was called (it handles the stream conversion logic internally? No, service does it)
        # The service converts bytes to StringIO before passing to parser
        # We can verify by checking if parser.parse was called with a StringIO
        args, _ = mock_parser.parse.call_args
        assert isinstance(args[0], io.StringIO)

    def test_process_academic_csv_student_not_found(self, service, mock_student_repo):
        csv_content = "student_id,module_code,type,value,date\nS99,M1,grade,80,2023-01-01"
        file_stream = io.StringIO(csv_content)
        
        mock_student_repo.get_by_student_id.return_value = None
        
        result = service.process_academic_csv(file_stream)
        
        assert result['errors'] == 1
        assert "Student not found" in result['details'][0]

    def test_process_academic_csv_module_not_found(self, service, mock_student_repo, mock_user_repo):
        csv_content = "student_id,module_code,type,value,date\nS1,M99,grade,80,2023-01-01"
        file_stream = io.StringIO(csv_content)
        
        mock_student_repo.get_by_student_id.return_value = MagicMock()
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = None
        
        result = service.process_academic_csv(file_stream)
        
    def test_process_user_csv_bytes_io(self, service, mock_parser):
        mock_parser.parse.return_value = []
        file_stream = io.BytesIO(b"username,password")
        
        service.process_user_csv(file_stream)
        
        # Should hit the TextIOWrapper path
        args, _ = mock_parser.parse.call_args
        assert isinstance(args[0], io.TextIOWrapper)

    def test_process_academic_csv_no_seek(self, service, mock_student_repo, mock_user_repo):
        # Mock a stream without seek
        file_stream = MagicMock()
        file_stream.read.return_value = "student_id,module_code,type,value,date\n"
        del file_stream.seek
        
        # We need to ensure it behaves like a text stream or handle the wrapper check
        # If we want to hit line 145 (if hasattr seek), we need it to NOT have seek.
        # But DictReader needs an iterator.
        file_stream.__iter__.return_value = ["student_id,module_code,type,value,date", "S1,M1,grade,80,2023-01-01"]
        
        mock_student = MagicMock()
        mock_student.id = 1
        mock_student_repo.get_by_student_id.return_value = mock_student
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        result = service.process_academic_csv(file_stream)
        
        assert result['success'] == 1

    def test_process_academic_csv_with_seek(self, service, mock_student_repo, mock_user_repo):
        # Use real StringIO which has seek
        csv_content = "student_id,module_code,type,value,date\nS1,M1,grade,80,2023-01-01"
        file_stream = io.StringIO(csv_content)
        
        mock_student = MagicMock()
        mock_student.id = 1
        mock_student_repo.get_by_student_id.return_value = mock_student
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        result = service.process_academic_csv(file_stream)
        
        assert result['success'] == 1
        # seek(0) is called internally, we can't assert it on real object easily unless we wrap it
        # but coverage should pick it up.

    def test_process_academic_csv_no_seek(self, service, mock_student_repo, mock_user_repo):
        # Create a custom class that behaves like a stream but has no seek
        class NoSeekStream:
            def __init__(self, content):
                self.lines = content.splitlines(keepends=True)
                self.iter = iter(self.lines)
            
            def read(self, size=-1):
                # Simple read implementation for check
                return "".join(self.lines)
            
            def __iter__(self):
                return self.iter
        
        csv_content = "student_id,module_code,type,value,date\nS1,M1,grade,80,2023-01-01"
        file_stream = NoSeekStream(csv_content)
        
        mock_student = MagicMock()
        mock_student.id = 1
        mock_student_repo.get_by_student_id.return_value = mock_student
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        result = service.process_academic_csv(file_stream)
        
        assert result['success'] == 1

    def test_process_academic_csv_commit_exception(self, service, mock_student_repo, mock_user_repo):
        csv_content = "student_id,module_code,type,value,date\nS1,M1,grade,80,2023-01-01"
        file_stream = io.StringIO(csv_content)
        
        mock_student_repo.get_by_student_id.return_value = MagicMock()
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        # Mock db_session.commit to raise exception (outer try/except)
        mock_user_repo.session.commit.side_effect = Exception("Commit Error")
        
        with pytest.raises(Exception, match="Commit Error"):
            service.process_academic_csv(file_stream)
        
        mock_user_repo.session.rollback.assert_called()

    def test_process_academic_csv_loop_exception(self, service, mock_student_repo, mock_user_repo):
        csv_content = "student_id,module_code,type,value,date\nS1,M1,grade,80,2023-01-01"
        file_stream = io.StringIO(csv_content)
        
        mock_student_repo.get_by_student_id.return_value = MagicMock()
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        # Mock db_session.add to raise exception
        mock_user_repo.session.add.side_effect = Exception("DB Error")
        
        result = service.process_academic_csv(file_stream)
        
        assert result['errors'] == 1
        assert "Row error: DB Error" in result['details'][0]

    def test_process_academic_csv_bytes_io(self, service, mock_student_repo, mock_user_repo):
        csv_content = b"student_id,module_code,type,value,date\nS1,M1,grade,80,2023-01-01"
        file_stream = io.BytesIO(csv_content)
        
        mock_student = MagicMock()
        mock_student.id = 1
        mock_student_repo.get_by_student_id.return_value = mock_student
        mock_user_repo.session.query.return_value.filter_by.return_value.first.return_value = MagicMock()
        
        result = service.process_academic_csv(file_stream)
        
        assert result['success'] == 1

    def test_process_academic_csv_missing_columns(self, service):
        csv_content = "student_id,type,value,date\nS1,grade,80,2023-01-01" # Missing module_code
        file_stream = io.StringIO(csv_content)
        
        with pytest.raises(ValueError, match="Missing required columns"):
            service.process_academic_csv(file_stream)
