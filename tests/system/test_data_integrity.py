import pytest
from src.models.user import User
from src.models.student import Student
from src.services.admin_service import AdminService
from src.repositories.user_repository import UserRepository

@pytest.mark.system
class TestDataIntegrity:
    def test_cascade_delete_integrity(self, db_session):
        """
        System test to ensure that deleting a User correctly removes the associated Student record.
        """
        # 1. Create User and Student
        user = User(username="integrity_user", role="STUDENT")
        user.set_password("password")
        db_session.add(user)
        db_session.flush()
        
        student = Student(
            student_id="INT001", 
            name="Integrity Test", 
            email="integrity@test.com",
            user_id=user.id # Link via FK
        )
        db_session.add(student)
        db_session.commit()
        
        # Capture IDs before deletion
        user_id = user.id
        student_id = student.id

        # 2. Delete User via Service
        user_repo = UserRepository(db_session)
        admin_service = AdminService(user_repo)
        admin_service.hard_delete_user(user_id)
        
        # 3. Verify Cascade
        # User should be gone
        assert db_session.query(User).filter_by(id=user_id).first() is None
        
        # Student should be gone (Cascade)
        deleted_student = db_session.query(Student).filter_by(id=student_id).first()
        assert deleted_student is None, "Student record should have been cascade deleted"
