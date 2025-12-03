import pytest
import io
from src.utils.parsers import UserCSVParser

class TestParsers:
    def test_user_csv_parser_missing_headers(self):
        parser = UserCSVParser()
        # Empty file results in no fieldnames
        file_stream = io.StringIO("")
        with pytest.raises(ValueError, match="Missing required columns"):
            parser.parse(file_stream)
            
    def test_user_csv_parser_wrong_headers(self):
        parser = UserCSVParser()

    def test_abstract_parser(self):
        from src.utils.parsers import AbstractParser
        class ConcreteParser(AbstractParser):
            def parse(self, file_stream):
                return super().parse(file_stream)
        
        parser = ConcreteParser()
        assert parser.parse(None) is None

    def test_grade_csv_parser_missing_headers(self):
        from src.utils.parsers import GradeCSVParser
        parser = GradeCSVParser()
        file_stream = io.StringIO("student_id,grade") # Missing module_code
        with pytest.raises(ValueError, match="Missing required columns"):
            parser.parse(file_stream)

    def test_attendance_csv_parser_missing_headers(self):
        from src.utils.parsers import AttendanceCSVParser
        parser = AttendanceCSVParser()
        file_stream = io.StringIO("student_id,date") # Missing module_code, status
        with pytest.raises(ValueError, match="Missing required columns"):
            parser.parse(file_stream)

    def test_survey_csv_parser_missing_headers(self):
        from src.utils.parsers import SurveyCSVParser
        parser = SurveyCSVParser()
        file_stream = io.StringIO("student_id,week") # Missing stress, sleep
        with pytest.raises(ValueError, match="Missing required columns"):
            parser.parse(file_stream)
