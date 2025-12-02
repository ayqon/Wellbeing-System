from sqlalchemy import Column, String
from src.models.base import BaseModel, TimestampMixin

class SystemConfig(BaseModel, TimestampMixin):
    """
    System configuration model for storing key-value pairs.
    Used for global settings like academic year start/end dates.
    """
    __tablename__ = 'system_config'

    key = Column(String(50), primary_key=True)
    value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

    def __init__(self, key, value, description=None):
        self.key = key
        self.value = value
        self.description = description
