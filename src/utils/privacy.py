import hashlib
import secrets

class Anonymizer:
    def __init__(self):
        self._salt = secrets.token_hex(16)

    def mask_identity(self, user_id: str) -> str:
        """
        Masks the user identity using a salted hash.
        """
        salted_input = f"{user_id}{self._salt}".encode('utf-8')
        return hashlib.sha256(salted_input).hexdigest()
