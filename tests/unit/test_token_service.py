import pytest
import jwt
import datetime
from src.services.token_service import TokenService

class TestTokenService:
    def test_create_token(self):
        token = TokenService.create_token("user1", "STUDENT")
        assert isinstance(token, str)
        
        # Decode to verify payload
        payload = jwt.decode(token, TokenService.SECRET_KEY, algorithms=[TokenService.ALGORITHM])
        assert payload['sub'] == "user1"
        assert payload['role'] == "STUDENT"

    def test_verify_token_valid(self):
        token = TokenService.create_token("user1", "STUDENT")
        payload = TokenService.verify_token(token)
        assert payload is not None
        assert payload['sub'] == "user1"

    def test_verify_token_expired(self):
        # Manually create an expired token
        payload = {
            "sub": "user1",
            "role": "STUDENT",
            "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM)
        
        result = TokenService.verify_token(token)
        assert result is None

    def test_verify_token_invalid(self):
        token = "invalid.token.string"
        result = TokenService.verify_token(token)
        assert result is None
