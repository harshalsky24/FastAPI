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
def test_user_data():
    """Test user data."""
    return {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "newpassword"
    }

def test_register_user(db_session, test_user_data):
    # Step 1: Send POST request to the /register endpoint
    response = client.post("/register", json=test_user_data)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    response_data = response.json()
    
    # Step 2: Verify response data
    assert response_data["username"] == test_user_data["username"]
    assert response_data["email"] == test_user_data["email"]

    # Step 3: Verify user is created in the database
    db_user = db_session.query(User).filter(User.username == "newuser").first()
    assert db_user is not None, "User should exist in the database"
    assert db_user.username == test_user_data["username"]
    assert db_user.email == test_user_data["email"]
    assert get_password_hash(test_user_data["password"]) != test_user_data["password"]

@pytest.fixture(scope="function", autouse=True)
def cleanup_test_user(db_session, test_user_data):
    """Clean up the test user after each test."""
    yield
    db_session.query(User).filter(User.username == test_user_data["username"]).delete()
    db_session.commit()
