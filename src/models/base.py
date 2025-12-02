from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Boolean

Base = declarative_base()

class BaseModel(Base):
    """
    Abstract base model for all entities.
    """
    __abstract__ = True

class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps.
    """
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class SoftDeleteMixin:
    """
    Mixin to add soft delete functionality.
    """
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        """Mark the record as deleted."""
        self.is_active = False
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_active = True
        self.deleted_at = None