import pytest
import io
from src.services.user_csv_parser import UserCSVParser

class TestUserCSVParser:
    def test_parse_valid_csv(self):
        csv_content = "username,password,role,student_id,name,email\nuser1,pass1,STUDENT,S1,User One,u1@example.com"
        file_stream = io.StringIO(csv_content)
        
        parser = UserCSVParser()
        result = parser.parse(file_stream)
        
        assert len(result) == 1
        assert result[0]['username'] == 'user1'
        assert result[0]['role'] == 'STUDENT'

    def test_parse_missing_columns(self):
        csv_content = "username,password\nuser1,pass1"
        file_stream = io.StringIO(csv_content)
        
        parser = UserCSVParser()
        with pytest.raises(ValueError, match="Missing required columns"):
            parser.parse(file_stream)

    def test_parse_empty_file(self):
        file_stream = io.StringIO("")
        
        parser = UserCSVParser()
        with pytest.raises(ValueError, match="Missing required columns"):
            parser.parse(file_stream)

    def test_parse_reset_stream(self):
        csv_content = "username,password,role,student_id,name,email\nuser1,pass1,STUDENT,S1,User One,u1@example.com"
        file_stream = io.StringIO(csv_content)
        file_stream.read() # Move to end
        
        parser = UserCSVParser()
        result = parser.parse(file_stream)
        
        assert len(result) == 1
