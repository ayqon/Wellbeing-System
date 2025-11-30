from datetime import datetime, timezone
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, DateTime, Boolean

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

class TimestampMixin:
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

class SoftDeleteMixin:
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self):
        self.is_active = True
        self.deleted_at = None