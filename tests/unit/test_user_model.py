import pytest
from src.models import User


def test_user_password_hashing():
    """Test that password hashing works correctly."""
    user = User(username="testuser", role="student")
    user.set_password("securepassword")
    
    assert user.password_hash is not None
    assert user.password_hash != "securepassword"
    assert user.check_password("securepassword") is True
    assert user.check_password("wrongpassword") is False


def test_user_creation():
    """Test user creation with basic attributes."""
    user = User(username="testuser", role="student")
    assert user.username == "testuser"
    assert user.role == "student"


def test_user_soft_delete():
    """Test soft delete functionality."""
    user = User(username="testuser", role="student", is_active=True)
    assert user.is_active is True
    assert user.deleted_at is None

    user.soft_delete()
    assert user.is_active is False
    assert user.deleted_at is not None

    user.restore()
    assert user.is_active is True
    assert user.deleted_at is None
