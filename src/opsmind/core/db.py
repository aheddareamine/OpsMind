from sqlalchemy import create_engine
from opsmind.core.config import get_settings
from sqlalchemy.orm import sessionmaker


settings = get_settings()
engine = create_engine(
    url=settings.database_url,
    pool_size=5,
    max_overflow=10
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()