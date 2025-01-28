import pytest
from fastapi.testclient import TestClient
from task.main import app
from task.database import SessionLocal
from task.models import User
from task.hashing import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Provides a database session for tests and handles cleanup."""
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="function")
def test_user(db_session):
    """Sets up a test user in the database."""
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(test_user)
    db_session.commit()
    yield test_user
    db_session.query(User).filter(User.username == "testuser").delete()
    db_session.commit()

def test_login_user_success(db_session, test_user):
    """Test login with valid credentials."""
    valid_credentials = {
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    response = client.post("/login", json=valid_credentials)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_invalid_password(db_session, test_user):
    """Test login with an invalid password."""
    invalid_credentials = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/login", json=invalid_credentials)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.json()["detail"] == "Invalid credentials"

def test_login_non_existent_user(db_session):
    """Test login with a non-existent email."""
    non_existent_user = {
        "email": "wronguser@example.com",
        "password": "testpassword"
    }
    response = client.post("/login", json=non_existent_user)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.json()["detail"] == "Invalid credentials"
