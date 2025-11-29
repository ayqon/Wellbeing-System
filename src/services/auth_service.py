import jwt
import datetime
from src.models.user import User

class AuthService:
    """
    Service for handling user authentication.
    """
    
    SECRET_KEY = "dev_secret_key"  # TODO: Move to config
    ALGORITHM = "HS256"

    def __init__(self, user_repo):
        """
        Initialize AuthService with a user repository.
        
        Args:
            user_repo: Repository for accessing user data.
        """
        self.user_repo = user_repo

    def login(self, username, password):
        """
        Authenticate a user and return a JWT token.
        
        Args:
            username (str): The username.
            password (str): The password.
            
        Returns:
            str: JWT token.
            
        Raises:
            ValueError: If authentication fails.
        """
        user = self.user_repo.get_by_username(username)
        
        if not user or not user.check_password(password):
            raise ValueError("Invalid username or password")
            
        # Generate Token
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token
