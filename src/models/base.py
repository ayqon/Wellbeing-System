from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.orm import Session
from src.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)

class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> T:
        pass

    @abstractmethod
    def get(self, id: Any) -> Optional[T]:
        pass

    @abstractmethod
    def list(self) -> List[T]:
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, id: Any) -> bool:
        pass

class SqlAlchemyRepository(AbstractRepository[T]):
    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def add(self, entity: T) -> T:
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def get(self, id: Any) -> Optional[T]:
        return self.session.query(self.model).filter(self.model.id == id).first()

    def list(self) -> List[T]:
        return self.session.query(self.model).all()

    def update(self, entity: T) -> T:
        self.session.merge(entity)
        self.session.commit()
        return entity

    def delete(self, id: Any) -> bool:
        entity = self.get(id)
        if entity:
            self.session.delete(entity)
            self.session.commit()
            return True
        return False