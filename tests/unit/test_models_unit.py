import pytest
from src.models.student import Student
from src.models.academic import Course, Module, StudentModule, ModuleGrade, AttendanceRegister
from src.models.survey import WellbeingSurvey, SurveyStatus
from src.models.user import User
from datetime import datetime

class TestModels:
    def test_student_repr(self):
        s = Student(student_id="s1", name="n1", email="e1")
        assert "s1" in repr(s)
        
    def test_student_increment_misses(self):
        s = Student(student_id="s1", name="n1", email="e1")
        s.increment_misses()
        assert s.missed_surveys == 1
        
    def test_student_reset_misses(self):
        s = Student(student_id="s1", name="n1", email="e1")
        s.increment_misses()
        s.reset_misses()
        assert s.missed_surveys == 0

    def test_course_repr(self):
        c = Course(course_code="C1", name="N1")
        assert "C1" in repr(c)

    def test_module_repr(self):
        m = Module(module_code="M1", name="N1", course=None)
        assert "M1" in repr(m)

    def test_student_module_repr(self):
        sm = StudentModule(student=None, module=None)
        assert "StudentModule" in repr(sm)

    def test_module_grade_repr(self):
        mg = ModuleGrade(student_id=1, module_id=1, grade=80)
        assert "80" in repr(mg)

    def test_attendance_repr(self):
        ar = AttendanceRegister(student_id=1, module_id=1, date=datetime.now(), status="Present")
        assert "Present" in repr(ar)

    def test_user_password(self):
        u = User(username="u", password_hash="hash", role="STUDENT")
        u.set_password("password")
        assert u.check_password("password")
        assert not u.check_password("wrong")
