import pytest
from unittest.mock import Mock
from src.services.auth_service import AuthService
from src.models.user import User

class TestAuthService:
    """Test suite for AuthService."""

    @pytest.fixture
    def mock_user_repo(self):
        """Fixture for mocked UserRepository."""
        return Mock()

    @pytest.fixture
    def auth_service(self, mock_user_repo):
        """Fixture for AuthService instance."""
        return AuthService(user_repo=mock_user_repo)

    def test_login_success(self, auth_service, mock_user_repo):
        """Test successful login returns a token."""
        # Arrange
        username = "testuser"
        password = "password123"
        user = User(username=username, role="student")
        user.set_password(password)
        mock_user_repo.get_by_username.return_value = user

        # Act
        token = auth_service.login(username, password)

        # Assert
        assert token is not None
        assert isinstance(token, str)
        mock_user_repo.get_by_username.assert_called_once_with(username)

    def test_login_failure_invalid_username(self, auth_service, mock_user_repo):
        """Test login fails when user does not exist."""
        # Arrange
        mock_user_repo.get_by_username.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid username or password"):
            auth_service.login("nonexistent", "password")

    def test_login_failure_invalid_password(self, auth_service, mock_user_repo):
        """Test login fails when password is incorrect."""
        # Arrange
        username = "testuser"
        password = "password123"
        user = User(username=username, role="student")
        user.set_password(password)
        mock_user_repo.get_by_username.return_value = user

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid username or password"):
            auth_service.login(username, "wrongpassword")
