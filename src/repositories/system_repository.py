from src.repositories.base import SqlAlchemyRepository
from src.models.system import SystemConfig

class SystemRepository(SqlAlchemyRepository):
    """
    Repository for SystemConfig entity.
    """
    def __init__(self, session):
        super().__init__(session, SystemConfig)

    def get(self, key):
        """Get config by key."""
        return self.session.query(SystemConfig).filter_by(key=key).first()
