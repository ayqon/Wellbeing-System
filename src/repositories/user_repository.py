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

    def get_by_username(self, username: str) -> User:
        """
        Retrieve a user by their username.

        Args:
            username (str): The username to search for.

        Returns:
            User: The user object if found, else None.
        """
        return self.session.query(User).filter_by(username=username).first()
