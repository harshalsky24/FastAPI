import pytest
from fastapi.testclient import TestClient
from task.main import app
from task.database import SessionLocal
from task.models import User, Team
from task.hashing import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Provides a database session for tests and handles cleanup."""
    db = SessionLocal()
    yield db
    db.rollback()
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

def test_create_team_success(db_session, test_user):
    """Test creating a team successfully."""
    # Login to get the authentication token
    valid_credentials = {
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    response = client.post("/login", json=valid_credentials)
    token = response.json()["access_token"]

    # Create a team with valid data
    team_data = {
        "name": "Test Team"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/team-create", json=team_data, headers=headers)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "team" in data
    assert data["message"] == "Team created Successfully."
    assert data["team"]["name"] == team_data["name"]

    # Cleanup the created team
    db_session.query(Team).filter(Team.name == "Test Team").delete()
    db_session.commit()


def test_create_team_duplicate_name(db_session, test_user):
    """Test creating a team with an existing name."""
    # Login to get the authentication token
    valid_credentials = {
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    response = client.post("/login", json=valid_credentials)
    token = response.json()["access_token"]

    # Create the first team
    team_data = {
        "name": "Test Team"
    }
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/team-create", json=team_data, headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    # Try to create the same team again (duplicate name)
    response = client.post("/team-create", json=team_data, headers=headers)
    assert response.status_code == 400, f"Expected 400, got {response.status_code}"
    assert response.json()["detail"] == "Team with this name already exist"

    # Cleanup the created team
    db_session.query(Team).filter(Team.name == "Test Team").delete()
    db_session.commit()
