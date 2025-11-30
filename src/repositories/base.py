from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from src.models.base import BaseModel

# Define a generic type variable T that must be a subclass of BaseModel.
# This ensures that our repositories only work with our application's models.
T = TypeVar("T", bound=BaseModel)

class AbstractRepository(ABC, Generic[T]):
    """
    Abstract base class for the Repository pattern.
    
    This class defines the interface that all concrete repositories must implement.
    It provides a standard set of CRUD (Create, Read, Update, Delete) operations
    to abstract the underlying data access logic from the business logic.
    """

    @abstractmethod
    def add(self, entity: T) -> T:
        """
        Add a new entity to the repository.

        Args:
            entity (T): The entity instance to add.

        Returns:
            T: The added entity, potentially with updated fields (e.g., auto-generated ID).
        """
        pass

    @abstractmethod
    def get(self, id: Any) -> Optional[T]:
        """
        Retrieve an entity by its unique identifier.

        Args:
            id (Any): The unique identifier of the entity.

        Returns:
            Optional[T]: The entity if found, otherwise None.
        """
        pass

    @abstractmethod
    def list(self) -> List[T]:
        """
        Retrieve all entities from the repository.

        Returns:
            List[T]: A list of all entities.
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """
        Update an existing entity in the repository.

        Args:
            entity (T): The entity with updated values.

        Returns:
            T: The updated entity.
        """
        pass

    @abstractmethod
    def delete(self, id: Any) -> bool:
        """
        Delete an entity by its unique identifier.

        Args:
            id (Any): The unique identifier of the entity to delete.

        Returns:
            bool: True if the entity was successfully deleted, False if it was not found.
        """
        pass

class SqlAlchemyRepository(AbstractRepository[T]):
    """
    Concrete implementation of AbstractRepository using SQLAlchemy.
    
    This class provides the actual database interactions for SQLAlchemy models.
    It manages the SQLAlchemy session and performs database operations.
    """

    def __init__(self, session: Session, model: Type[T]):
        """
        Initialize the SqlAlchemyRepository.

        Args:
            session (Session): The SQLAlchemy database session.
            model (Type[T]): The SQLAlchemy model class this repository manages.
        """
        self.session = session
        self.model = model

    def add(self, entity: T) -> T:
        """
        Add a new entity to the database.
        """
        self.session.add(entity)
        # Commit the transaction to save changes to the database
        self.session.commit()
        # Refresh the instance to load any new data from the database, 
        # such as the auto-generated ID or default values.
        self.session.refresh(entity)
        return entity

    def get(self, id: Any) -> Optional[T]:
        """
        Retrieve an entity by ID from the database.
        """
        # Use query.filter to find the entity with the matching ID.
        # .first() returns the first result or None if no match is found.
        return self.session.query(self.model).filter(self.model.id == id).first()

    def list(self) -> List[T]:
        """
        Retrieve all entities of this model type from the database.
        """
        # .all() returns a list of all records found in the table.
        return self.session.query(self.model).all()

    def update(self, entity: T) -> T:
        """
        Update an existing entity in the database.
        """
        # merge() copies the state of the given instance into a persistent instance 
        # with the same identifier. If the instance is not in the session, it is added.
        self.session.merge(entity)
        self.session.commit()
        return entity

    def delete(self, id: Any) -> bool:
        """
        Delete an entity by ID from the database.
        """
        # First, retrieve the entity to ensure it exists and to attach it to the session.
        entity = self.get(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        # Return False if the entity was not found, indicating no deletion occurred.
        return False