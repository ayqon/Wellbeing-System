import jwt
import datetime
from typing import Optional

class TokenService:
    """
    Service for generating and verifying JWT tokens.
    """
    SECRET_KEY = "dev_secret_key"
    ALGORITHM = "HS256"

    @staticmethod
    def create_token(user_id: str, role: str) -> str:
        """
        Create a JWT token for a user.
        """
        payload = {
            "sub": user_id,
            "role": role,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        return jwt.encode(payload, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        """
        Verify a JWT token and return the payload.
        """
        try:
            return jwt.decode(token, TokenService.SECRET_KEY, algorithms=[TokenService.ALGORITHM])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
