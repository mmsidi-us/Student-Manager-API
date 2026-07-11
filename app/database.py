# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all models
class Base(DeclarativeBase):
    pass

# app/database.py (add this function)
def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db       # Give the session to the endpoint
    finally:
        db.close()     # Always close it when the request is done