import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from task.main import app  # FastAPI app instance
from task.database import get_db, SessionLocal
from task.models import Team, Task, TeamMembership, Role, User
from task.hashing import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh database session for each test."""
    db = SessionLocal()
    yield db
    db.rollback()
    db.close()

@pytest.fixture(scope="function")
def setup_data(db_session):
    """Setup test data: User, Team, Role, and Membership before running the test."""
    
    # Create a test user
    test_user = User(
        username="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(test_user)
    db_session.commit()
    db_session.refresh(test_user)

    # Create a test team
    test_team = Team(name="Test Team")
    db_session.add(test_team)
    db_session.commit()
    db_session.refresh(test_team)

    # Assign a role
    test_role = Role(role_name="admin")
    db_session.add(test_role)
    db_session.commit()
    db_session.refresh(test_role)

    # Add user to the team with role
    team_membership = TeamMembership(team_id=test_team.id, user_id=test_user.id, role_id=test_role.id)
    db_session.add(team_membership)
    db_session.commit()

    yield {
        "user": test_user,
        "team": test_team,
        "role": test_role
    }

    # Cleanup
    db_session.query(TeamMembership).filter_by(team_id=test_team.id).delete()
    db_session.query(Task).filter_by(team_id=test_team.id).delete()
    db_session.query(Role).filter_by(id=test_role.id).delete()
    db_session.query(Team).filter_by(id=test_team.id).delete()
    db_session.query(User).filter_by(id=test_user.id).delete()
    db_session.commit()


def test_create_task(db_session, setup_data):
    """Test creating a new task successfully."""

    test_user = setup_data["user"]
    test_team = setup_data["team"]

    # Step 1: Log in to get JWT token
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    login_response = client.post("/login", json=login_data)
    
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Prepare Task Data
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "In Review",
        "priority": "High",
        "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "reviewer_id": test_user.id,
        "assignee_id": test_user.id
    }

    # Step 3: Send Request to Create Task
    response = client.post(f"/task/{test_team.id}/create-task", json=task_data, headers=headers)

    # Step 4: Validate Response
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    
    response_data = response.json()
    assert response_data["title"] == task_data["title"]
    assert response_data["description"] == task_data["description"]
    assert response_data["status"] == task_data["status"]
    assert response_data["priority"] == task_data["priority"]
    assert response_data["deadline"] == task_data["deadline"]
    assert response_data["reviewer_id"] == task_data["reviewer_id"]
    assert response_data["assignee_id"] == task_data["assignee_id"]

    # Step 5: Cleanup the created task
    created_task = db_session.query(Task).filter_by(title=task_data["title"]).first()
    if created_task:
        db_session.delete(created_task)
        db_session.commit()
