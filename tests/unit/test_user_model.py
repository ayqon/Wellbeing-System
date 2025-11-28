import pytest
from src.models.user import User


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
