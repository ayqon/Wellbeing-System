from sqlalchemy import Column, String, Integer
from src.models.base import BaseModel, TimestampMixin, SoftDeleteMixin
import bcrypt

class User(BaseModel, TimestampMixin, SoftDeleteMixin):
    """
    User entity representing a system user (Student, Officer, or Director).
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(20), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)

    def set_password(self, password):
        """Hashes and sets the user's password."""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Verifies the provided password against the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
