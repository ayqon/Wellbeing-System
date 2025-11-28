from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Database:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        # TODO: Move URL to config
        self.DATABASE_URL = "sqlite:///./swats.db"
        self.engine = create_engine(
            self.DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
        self.SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=self.engine
        )

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
