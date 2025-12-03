import pytest
from unittest.mock import MagicMock
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

    def test_process_user_csv_bytes_input(self, service, mock_parser, mock_user_repo, mock_student_repo):
        mock_parser.parse.return_value = []
        file_stream = b"username,password"
        
        service.process_user_csv(file_stream)
        
        # Verify parser was called (it handles the stream conversion logic internally? No, service does it)
        # The service converts bytes to StringIO before passing to parser
        # We can verify by checking if parser.parse was called with a StringIO
        args, _ = mock_parser.parse.call_args
        assert isinstance(args[0], io.StringIO)

    def test_process_user_csv_bytes_io(self, service, mock_parser):
        mock_parser.parse.return_value = []
        file_stream = io.BytesIO(b"username,password")
        
        service.process_user_csv(file_stream)
        
        # Should hit the TextIOWrapper path
        args, _ = mock_parser.parse.call_args
        assert isinstance(args[0], io.TextIOWrapper)
