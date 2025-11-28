from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.models.base import BaseModel


class Course(BaseModel):
    """
    Course model representing an academic course.
    
    OOP Principle: Encapsulation - Course manages its relationship with modules
    """
    __tablename__ = 'courses'

    # Primary key - manually added since BaseModel is empty
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps - track when record is created and updated
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    # Business fields
    course_code = Column(String(20), unique=True, nullable=False)  # e.g., "AAI"
    name = Column(String(100), nullable=False)  # e.g., "Applied Artificial Intelligence"
    director_user_id = Column(Integer, nullable=True)  # Optional: FK to User table

    # Relationships - SQLAlchemy manages the collection automatically
    modules = relationship(
        "Module",
        back_populates="course",
        cascade="all, delete-orphan"  # Delete modules when course is deleted
    )

    def __init__(self, course_code, name, director_user_id=None):
        """
        Initialize a Course object.
        
        Args:
            course_code (str): Unique course code (e.g., "AAI")
            name (str): Course name
            director_user_id (int, optional): ID of course director
        """
        self.course_code = course_code
        self.name = name
        self.director_user_id = director_user_id

    def __repr__(self) -> str:
        """String representation for debugging purposes."""
        return f"<Course {self.course_code}: {self.name}>"


class Module(BaseModel):
    """
    Module model representing a module within a course.
    
    OOP Principle: Inheritance - Inherits abstract base from BaseModel
    OOP Principle: Association - Module belongs to a Course
    """
    __tablename__ = 'modules'

    # Primary key - manually added since BaseModel is empty
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps - track when record is created and updated
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    # Business fields
    module_code = Column(String(20), unique=True, nullable=False)  # e.g., "WM9QF"
    name = Column(String(100), nullable=False)  # e.g., "Programming for AI"
    leader_user_id = Column(Integer, nullable=True)  # Optional: FK to User table
    
    # Foreign key - links to parent Course
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)

    # Relationships
    course = relationship("Course", back_populates="modules")  # Many-to-one with Course
    student_enrollments = relationship(
        "StudentModule",
        back_populates="module",
        cascade="all, delete-orphan"  # Delete enrollments when module is deleted
    )

    def __init__(self, module_code, name, course, leader_user_id=None):
        """
        Initialize a Module object.
        
        Args:
            module_code (str): Unique module code (e.g., "WM9QF")
            name (str): Module name
            course (Course): Parent Course object (SQLAlchemy handles the FK)
            leader_user_id (int, optional): ID of module leader
        """
        self.module_code = module_code
        self.name = name
        self.course = course  # SQLAlchemy automatically sets course_id
        self.leader_user_id = leader_user_id

    def __repr__(self) -> str:
        """String representation for debugging purposes."""
        return f"<Module {self.module_code}: {self.name}>"


class StudentModule(BaseModel):
    """
    Association object representing enrollment of a student in a module.
    
    OOP Principle: Association Object Pattern
    This is more than a simple join table - it contains enrollment-specific data
    like semester and can be extended with grades, attendance, etc.
    """
    __tablename__ = 'student_modules'

    # Primary key - manually added since BaseModel is empty
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Timestamps - track when enrollment was created and updated
    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc), 
        nullable=False
    )
    
    # Foreign keys - links to Student and Module
    student_id = Column(Integer, ForeignKey('students.id'), nullable=False)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=False)
    
    # Enrollment-specific data
    semester = Column(String(20), nullable=True)  # e.g., "Fall 2025", "Spring 2026"

    # Relationships
    student = relationship("Student")  # One-way to Student (Student model doesn't have back_populates)
    module = relationship("Module", back_populates="student_enrollments")  # Bidirectional with Module

    def __init__(self, student, module, semester=None):
        """
        Initialize a StudentModule enrollment.
        
        Args:
            student (Student): Student object being enrolled
            module (Module): Module object student is enrolling in
            semester (str, optional): Semester of enrollment (e.g., "Fall 2025")
        """
        self.student = student  # SQLAlchemy automatically sets student_id
        self.module = module  # SQLAlchemy automatically sets module_id
        self.semester = semester

    def __repr__(self) -> str:
        """
        String representation for debugging purposes.
        Uses getattr to safely handle cases where IDs might not be set yet.
        """
        student_id = getattr(self.student, 'id', None)
        module_id = getattr(self.module, 'id', None)
        return f"<StudentModule student={student_id} module={module_id}>"