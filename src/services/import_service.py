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
        # We might still need db_session for academic import if we don't refactor that part yet,
        # or we can access it via repositories if needed, but for now let's assume repositories handle their own persistence
        # or share a session. Ideally, the service shouldn't know about db_session directly if using repositories.
        # However, for transaction management (commit/rollback), we might need access to the unit of work.
        # For this refactor, we'll assume the repositories share the session and we can commit via one of them 
        # or the caller handles the transaction. But to keep it simple and working with existing tests (which expect service to commit),
        # we'll access the session from the repository.
        self.db_session = self.user_repo.session

    def execute_import(self, file_stream):
        """
        Orchestrates the import process.
        Determines the type of import based on file content or context.
        For now, defaults to User import or checks headers.
        """
        # Simple heuristic: Check headers to decide strategy
        # Note: This consumes the stream, so we need to reset it
        if hasattr(file_stream, 'read') and hasattr(file_stream, 'seek'):
            pos = file_stream.tell()
            header_line = file_stream.readline()
            if isinstance(header_line, bytes):
                 header_line = header_line.decode('utf-8')
            file_stream.seek(pos) # Reset

            if 'username' in header_line:
                return self.process_user_csv(file_stream)
            elif 'module_code' in header_line:
                return self.process_academic_csv(file_stream)
        
        # Fallback or error
        return self.process_user_csv(file_stream)

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

    def process_academic_csv(self, file_stream):
        """
        Process a CSV file containing academic data (grades or attendance).
        
        The CSV is expected to have the following columns:
        - student_id: ID of the student (must exist in DB)
        - module_code: Code of the module (must exist in DB)
        - type: 'grade' or 'attendance'
        - value: The grade value (0-100) or attendance status (e.g., 'Present')
        - date: Date of the record in YYYY-MM-DD format
        
        Args:
            file_stream: A file-like object containing the CSV data.
            
        Returns:
            dict: A summary of the import process containing success/error counts.
        """
        results = {"success": 0, "errors": 0, "details": []}
        
        try:
            # Reset stream position
            if hasattr(file_stream, 'seek'):
                file_stream.seek(0)
            
            # Ensure text mode
            if hasattr(file_stream, 'read') and isinstance(file_stream.read(0), bytes):
                 file_stream = io.TextIOWrapper(file_stream, encoding='utf-8')
            if hasattr(file_stream, 'seek'):
                file_stream.seek(0)
                
            reader = csv.DictReader(file_stream)
            
            # Validate headers
            required_columns = {'student_id', 'module_code', 'type', 'value', 'date'}
            if not reader.fieldnames or not required_columns.issubset(set(reader.fieldnames)):
                raise ValueError(f"Missing required columns. Expected: {required_columns}")

            for row in reader:
                try:
                    # Lookup Student by student_id
                    # Use repository if available, otherwise fallback to session query (or add method to student repo)
                    student = self.student_repo.get_by_student_id(row['student_id'])
                    if not student:
                        raise ValueError(f"Student not found: {row['student_id']}")

                    # Lookup Module by module_code
                    # We don't have a ModuleRepository injected yet, so we'll use the session directly for now
                    # or we should have injected it. For this task, we'll use session.
                    module = self.db_session.query(Module).filter_by(module_code=row['module_code']).first()
                    if not module:
                        raise ValueError(f"Module not found: {row['module_code']}")

                    # Parse date
                    date_obj = datetime.strptime(row['date'], '%Y-%m-%d')

                    # Handle different data types based on 'type' column
                    if row['type'] == 'grade':
                        grade = ModuleGrade(
                            student_id=student.id,
                            module_id=module.id,
                            grade=int(row['value'])
                        )
                        self.db_session.add(grade)
                    elif row['type'] == 'attendance':
                        attendance = AttendanceRegister(
                            student_id=student.id,
                            module_id=module.id,
                            date=date_obj,
                            status=row['value']
                        )
                        self.db_session.add(attendance)
                    else:
                        raise ValueError(f"Unknown type: {row['type']}")

                    results["success"] += 1
                except Exception as e:
                    results["errors"] += 1
                    results["details"].append(f"Row error: {str(e)}")
                    continue

            # Commit changes
            self.db_session.commit()

        except Exception as e:
            self.db_session.rollback()
            raise e

        return results
