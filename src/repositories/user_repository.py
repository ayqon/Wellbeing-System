from sqlalchemy.orm import Session
from src.repositories.base import SqlAlchemyRepository
from src.models.user import User

class UserRepository(SqlAlchemyRepository[User]):
    """
    Repository for User entities.
    Inherits from SqlAlchemyRepository to provide standard CRUD operations.
    """
    def __init__(self, session: Session):
        """
        Initialize the UserRepository.

        Args:
            session (Session): The SQLAlchemy database session.
        """
        super().__init__(session, User)
