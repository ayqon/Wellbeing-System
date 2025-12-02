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

    def anonymize(self, students: list) -> list:
        """
        Converts a list of Student objects to anonymized dictionaries.
        
        Args:
            students (list): List of Student objects.
            
        Returns:
            list: List of anonymized student dictionaries.
        """
        anonymized = []
        for s in students:
            # Convert to dict
            s_dict = {
                "student_id": self.mask_identity(s.student_id),
                "name": None, # Redacted
                "email": None, # Redacted
                # Include metrics for risk calculation
                "stress": 0, # Placeholder, should come from surveys
                "sleep": 8, # Placeholder
                "misses": s.missed_surveys,
                "grade": 100.0, # Placeholder
                "attendance": 100, # Placeholder
                # Pass through risk score if already calculated (e.g. for testing)
                "cached_risk": s.current_risk_score 
            }
            
            anonymized.append(s_dict)
        return anonymized
