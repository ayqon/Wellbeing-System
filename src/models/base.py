from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    # Using integer ID for simplicity as per common practice, 
    # though UUIDs are also an option. Sticking to simple int for now.
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
