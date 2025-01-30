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


def test_delete_task(db_session, setup_data):
    """Test updating an existing task successfully."""
    
    test_user = setup_data["user"]
    test_team = setup_data["team"]

    # Step 1: Log in to get JWT token
    login_data = {"email": "testuser@example.com", "password": "testpassword"}
    login_response = client.post("/login", json=login_data)
    
    assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Create a task
    task_data = {
        "title": "Test Task",
        "description": "Initial description",
        "status": "In Review",
        "priority": "High",
        "deadline": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "creator_id": test_user.id,
        "reviewer_id": test_user.id,
        "assignee_id": test_user.id,
        "team": test_team.id
    }
    
    create_response = client.post(f"/task/{test_team.id}/create-task", json=task_data, headers=headers)
    assert create_response.status_code == 200, f"Task creation failed: {create_response.json()}"
    created_task = create_response.json()
    print(created_task)

    task_id = created_task["id"]
    print(task_id)
    team_id = test_team.id
    print(team_id)
     # Step 3: Send Request to Delete Task
    delete_payload = {"task_id": task_id}
    delete_response = client.request(method = "DELETE",
     url = f"/task/{test_team.id}/delete-task", 
     json=delete_payload, 
     headers=headers)
    
    # Step 4: Validate Response
    assert delete_response.status_code == 200, f"Expected 200, got {delete_response.status_code}"
    assert delete_response.json()["message"] == "Task Deleted"
    
    # Step 5: Ensure Task is Deleted
    deleted_task = db_session.query(Task).filter_by(id=task_id).first()
    assert deleted_task is None, "Task was not deleted"