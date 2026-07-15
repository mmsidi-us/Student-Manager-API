# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.utils.exceptions import AppException, NotFoundException

from app.main import app
from app.database import Base, get_db
from app.models.users import User
from app.utils.security import hash_password
from app.utils.limiter import limiter

# 1. Setup isolated in-memory database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function", autouse=True)
def disable_rate_limiting():
    """Disables rate limiting completely for all tests to prevent 429 errors."""
    limiter.enabled = False
    yield
    limiter.enabled = True


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create all tables before each test and drop them afterward."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides an isolated database session for a single test run."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function", autouse=True)
def override_database_dependency(db_session):
    """
    Globally overrides the database dependency for the entire duration of a test.
    This prevents individual fixtures from accidentally clearing overrides.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client():
    """Provides a TestClient instance."""
    return TestClient(app)


@pytest.fixture(scope="function")
def auth_headers(db_session, client):
    """Creates a mock user and returns valid OAuth2 Bearer authorization headers."""
    # Register mock admin user
    hashed_pwd = hash_password("secretpass123")
    test_user = User(username="testadmin", email="admin@example.com", hashed_password=hashed_pwd)
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)
    
    # Request Token via /auth/login (using the already-active global database override)
    response = client.post(
        "/auth/login",
        data={"grant_type": "password", "username": "testadmin", "password": "secretpass123"}
    )
    
    response_data = response.json()
    if "access_token" not in response_data:
        raise RuntimeError(f"Auth token generation failed in test setup. Response: {response_data}")
        
    token = response_data["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def sample_student(db_session):
    """Inserts a mock student into the test database for CRUD assertion."""
    from app.models.students import Student
    student = Student(
        name="Ahmed Ali",
        email="ahmed@example.com",
        grade_level=10,
        gpa=3.8,
        is_enrolled=True
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student