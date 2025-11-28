import pytest
from src.models.academic import Course, Module, StudentModule
from src.models.student import Student


class TestCourse:
    """Test suite for Course model."""

    def test_course_creation_with_all_fields(self):
        """Test Course object creation with all required fields."""
        course = Course(
            course_code="AAI",
            name="Applied Artificial Intelligence",
            director_user_id=1
        )
        assert course.course_code == "AAI"
        assert course.name == "Applied Artificial Intelligence"
        assert course.director_user_id == 1

    def test_course_creation_without_director(self):
        """Test Course can be created without a director."""
        course = Course(
            course_code="AAI",
            name="Applied Artificial Intelligence"
        )
        assert course.course_code == "AAI"
        assert course.director_user_id is None

    def test_course_string_representation(self):
        """Test Course __repr__ method."""
        course = Course(course_code="AAI", name="Applied Artificial Intelligence")
        assert str(course) == "<Course AAI: Applied Artificial Intelligence>"


class TestModule:
    """Test suite for Module model."""

    def test_module_creation_with_course(self):
        """Test Module creation with parent course relationship."""
        course = Course(course_code="AAI", name="Applied Artificial Intelligence")
        module = Module(
            module_code="WM9QF",
            name="Programming for Artificial Intelligence",
            course=course,
            leader_user_id=2
        )
        assert module.module_code == "WM9QF"
        assert module.name == "Programming for Artificial Intelligence"
        assert module.course == course
        assert module.leader_user_id == 2

    def test_module_belongs_to_course(self):
        """Test bidirectional relationship between module and course."""
        course = Course(course_code="AAI", name="Applied Artificial Intelligence")
        module = Module(
            module_code="WM9QF",
            name="Programming for Artificial Intelligence",
            course=course
        )
        # Module knows its course
        assert module.course == course
        # Course knows its modules
        assert module in course.modules

    def test_course_can_have_multiple_modules(self):
        """Test that a course can contain multiple modules."""
        course = Course(course_code="AAI", name="Applied Artificial Intelligence")
        module1 = Module(module_code="WM9QF", name="Programming for Artificial Intelligence", course=course)
        module2 = Module(module_code="WM9QE", name="Applied Statistics for Artificial Intelligence", course=course)
        
        assert len(course.modules) == 2
        assert module1 in course.modules
        assert module2 in course.modules


class TestStudentModule:
    """Test suite for StudentModule association object."""

    def test_student_module_creation(self):
        """Test StudentModule creation linking student to module."""
        student = Student(
            student_id="12345",
            name="Tom",
            email="tom@warwick.ac.uk"
        )
        course = Course(course_code="AAI", name="Applied Artificial Intelligence")
        module = Module(module_code="WM9QF", name="Programming for Artificial Intelligence", course=course)
        
        enrollment = StudentModule(
            student=student,
            module=module,
            semester="Fall 2025"
        )
        
        assert enrollment.student == student
        assert enrollment.module == module
        assert enrollment.semester == "Fall 2025"

    def test_student_module_without_semester(self):
        """Test StudentModule can be created without semester."""
        student = Student(
            student_id="12345",
            name="Tom",
            email="tom@warwick.ac.uk"
        )
        course = Course(course_code="AAI", name="Applied Artificial Intelligence")
        module = Module(module_code="WM9QF", name="Programming for Artificial Intelligence", course=course)
        
        enrollment = StudentModule(student=student, module=module)
        
        assert enrollment.semester is None

    def test_student_can_enroll_in_multiple_modules(self):
        """Test that a student can be enrolled in multiple modules."""
        student = Student(
            student_id="12345",
            name="Tom",
            email="tom@warwick.ac.uk"
        )
        course = Course(course_code="AAI", name="Applied Artificial Intelligence")
        module1 = Module(module_code="WM9QF", name="Programming for Artificial Intelligence", course=course)
        module2 = Module(module_code="WM9QE", name="Applied Statistics for Artificial Intelligence", course=course)
        
        enrollment1 = StudentModule(student=student, module=module1, semester="Fall 2025")
        enrollment2 = StudentModule(student=student, module=module2, semester="Fall 2025")
        
        assert enrollment1.student == student
        assert enrollment2.student == student
    
    def test_module_has_multiple_student_enrollments(self):
        """Test that a module can have multiple students enrolled."""
        course = Course(course_code="AAI", name="Applied AI")
        module = Module(module_code="WM9QF", name="Programming for AI", course=course)
        
        student1 = Student(student_id="12345", name="Tom", email="tom@warwick.ac.uk")
        student2 = Student(student_id="67890", name="Jane", email="jane@warwick.ac.uk")
        
        enrollment1 = StudentModule(student=student1, module=module, semester="Fall 2025")
        enrollment2 = StudentModule(student=student2, module=module, semester="Fall 2025")
        
        # Test Module can access its enrollments
        assert len(module.student_enrollments) == 2
        assert enrollment1 in module.student_enrollments
        assert enrollment2 in module.student_enrollments