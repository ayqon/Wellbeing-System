import csv
import io
from datetime import datetime
from src.models.user import User
from src.models.student import Student
from src.models.academic import ModuleGrade, AttendanceRegister, Module, Course, StudentModule

class ImportService:
    """
    Service responsible for importing data from CSV files into the database.
    
    This service handles parsing CSV content, validating structure, and creating
    associated database records for Users, Students, and Academic data (Grades/Attendance).
    It ensures transactional integrity by rolling back changes on error.
    """
    def __init__(self, user_repository, student_repository, user_csv_parser):
        """
        Initialize the ImportService with injected dependencies.
        
        Args:
            user_repository: Repository for User entity operations.
            student_repository: Repository for Student entity operations.
            user_csv_parser: Strategy for parsing User CSV files.
        """
        self.user_repo = user_repository
        self.student_repo = student_repository
        self.parser = user_csv_parser
        self.db_session = self.user_repo.session



    def process_user_csv(self, file_stream):
        """
        Process a CSV file containing user and student data using the injected parser and repositories.
        
        Args:
            file_stream: A file-like object containing the CSV data.
            
        Returns:
            dict: A summary of the import process.
        """
        results = {"success": 0, "errors": 0, "details": []}
        
        try:
            # Use the injected parser strategy
            # Ensure stream is text mode if parser expects it
            if isinstance(file_stream, bytes):
                 file_stream = io.StringIO(file_stream.decode('utf-8'))
            elif hasattr(file_stream, 'read') and isinstance(file_stream.read(0), bytes):
                 # It's a binary stream, wrap it
                 file_stream = io.TextIOWrapper(file_stream, encoding='utf-8')
            
            if hasattr(file_stream, 'seek'):
                file_stream.seek(0)

            rows = self.parser.parse(file_stream)

            for row in rows:
                try:
                    # Create User entity
                    user = User(
                        username=row['username'],
                        password_hash=row['password_hash'],
                        role=row['role']
                    )
                    self.user_repo.add(user)
                    self.user_repo.session.flush() # Get ID

                    # Create Student entity
                    student = Student(
                        student_id=row['student_id'],
                        name=row['name'],
                        email=row['email'],
                        user_id=user.id
                    )
                    self.student_repo.add(student)
                    
                    # Increment success counter
                    results["success"] += 1
                except Exception as e:
                    # Handle individual row errors
                    results["errors"] += 1
                    results["details"].append(f"Row error: {str(e)}")
                    self.db_session.rollback() # Rollback the specific row transaction
                    continue


            # Commit all successful changes
            self.db_session.commit()
            
        except Exception as e:
            # Rollback the entire session if a critical error occurs
            self.db_session.rollback()
            raise e

        return results

    def process_grade_csv(self, file_stream):
        """
        Process a CSV file containing grade data.
        """
        results = {"success": 0, "errors": 0, "details": []}
        try:
            # Reset stream
            if hasattr(file_stream, 'seek'): file_stream.seek(0)
            
            # Use local parser since we didn't inject it (simplification for now)
            from src.utils.parsers import GradeCSVParser
            parser = GradeCSVParser()
            rows = parser.parse(file_stream)

            for row in rows:
                try:
                    student = self.student_repo.get_by_student_id(row.student_id)
                    if not student: raise ValueError(f"Student not found: {row.student_id}")

                    module = self.db_session.query(Module).filter_by(module_code=row.module_code).first()
                    if not module: raise ValueError(f"Module not found: {row.module_code}")

                    grade = ModuleGrade(
                        student_id=student.id,
                        module_id=module.id,
                        grade=row.grade
                    )
                    self.db_session.add(grade)
                    results["success"] += 1
                except Exception as e:
                    results["errors"] += 1
                    results["details"].append(f"Row error: {str(e)}")
                    continue
            
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise e
        return results

    def process_attendance_csv(self, file_stream):
        """
        Process a CSV file containing attendance data.
        """
        results = {"success": 0, "errors": 0, "details": []}
        try:
            if hasattr(file_stream, 'seek'): file_stream.seek(0)
            
            from src.utils.parsers import AttendanceCSVParser
            parser = AttendanceCSVParser()
            rows = parser.parse(file_stream)

            for row in rows:
                try:
                    student = self.student_repo.get_by_student_id(row.student_id)
                    if not student: raise ValueError(f"Student not found: {row.student_id}")

                    module = self.db_session.query(Module).filter_by(module_code=row.module_code).first()
                    if not module: raise ValueError(f"Module not found: {row.module_code}")

                    date_obj = datetime.strptime(row.date, '%Y-%m-%d')
                    
                    attendance = AttendanceRegister(
                        student_id=student.id,
                        module_id=module.id,
                        date=date_obj,
                        status=row.status
                    )
                    self.db_session.add(attendance)
                    results["success"] += 1
                except Exception as e:
                    results["errors"] += 1
                    results["details"].append(f"Row error: {str(e)}")
                    continue
            
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise e
        return results

    def process_survey_csv(self, file_stream):
        """
        Process a CSV file containing survey data.
        """
        results = {"success": 0, "errors": 0, "details": []}
        try:
            if hasattr(file_stream, 'seek'): file_stream.seek(0)
            
            from src.utils.parsers import SurveyCSVParser
            from src.models.survey import WellbeingSurvey, SurveyStatus
            parser = SurveyCSVParser()
            rows = parser.parse(file_stream)

            for row in rows:
                try:
                    # Validate student exists (Survey uses student_id string FK)
                    student = self.student_repo.get_by_student_id(row.student_id)
                    if not student: raise ValueError(f"Student not found: {row.student_id}")

                    # Determine if critical
                    is_critical = row.stress > 4 or row.sleep < 4

                    survey = WellbeingSurvey(
                        student_id=row.student_id,
                        week=row.week,
                        year=datetime.now().year, # Default to current year for import
                        status=SurveyStatus.COMPLETED,
                        stress=row.stress,
                        sleep=row.sleep,
                        is_critical=is_critical
                    )
                    self.db_session.add(survey)
                    results["success"] += 1
                except Exception as e:
                    results["errors"] += 1
                    results["details"].append(f"Row error: {str(e)}")
                    continue
            
            self.db_session.commit()
        except Exception as e:
            self.db_session.rollback()
            raise e
        return results
