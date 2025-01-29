import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from task.main import app
from task.database import get_db, SessionLocal
from task.models import User, Team, Task, Role, TeamMembership
from task.hashing import get_password_hash
from datetime import datetime, timedelta
from task.auth import create_access_token

@pytest.fixture(scope="module")
def client():
    """Create a Test Client for FastAPI."""
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Provides a new test database session for each test."""
    db = SessionLocal()
    yield db
    db.rollback()  # Rollback any changes after test execution
    db.close()

@pytest.fixture(scope="function")
def setup_data(db_session):
    """Setup test data: Create User, Team, Role, and Membership."""

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

    # Add user to the team with a role
    team_membership = TeamMembership(team_id=test_team.id, user_id=test_user.id, role_id=test_role.id)
    db_session.add(team_membership)
    db_session.commit()

    yield {
        "user": test_user,
        "team": test_team,
        "role": test_role
    }

    # Cleanup after test
    db_session.query(TeamMembership).filter_by(team_id=test_team.id).delete()
    db_session.query(Task).filter_by(team_id=test_team.id).delete()
    db_session.query(Role).filter_by(id=test_role.id).delete()
    db_session.query(Team).filter_by(id=test_team.id).delete()
    db_session.query(User).filter_by(id=test_user.id).delete()
    db_session.commit()

def create_test_task(db_session: Session, user: User, team: Team, status="In Progress", priority="High"):
    """Helper function to create a test task."""
    task = Task(
        title="Test Task",
        description="This is a test task",
        status=status,
        priority=priority,
        assignee_id=user.id,
        deadline=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        reviewer_id=user.id,
        creator_id=user.id,
        team_id=team.id
    )
    db_session.add(task)
    db_session.commit()
    db_session.refresh(task)
    return task


def test_sort_filter(client, db_session, setup_data):
    """Test task sorting and filtering with authentication."""

    # Get user and team from setup data
    user = setup_data['user']
    team = setup_data['team']

    # Generate JWT Token for authentication
    token = create_access_token({"sub": str(user.id)}) 
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks
    task1 = create_test_task(db_session, user, team, status="In Progress", priority="High")
    task2 = create_test_task(db_session, user, team, status="Completed", priority="Medium")
    task3 = create_test_task(db_session, user, team, status="In Progress", priority="Low")

    # ✅ Test filtering by status
    response = client.get("/task/sortfilter?status=In Progress", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert all(task["status"] == "In Progress" for task in tasks)

    # ✅ Test filtering by priority
    response = client.get("/task/sortfilter?priority=High", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert all(task["priority"] == "High" for task in tasks)

    # ✅ Test filtering by assignee ID
    response = client.get(f"/task/sortfilter?assignee_id={user.id}", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert all(task["assignee_id"] == user.id for task in tasks)

    # ✅ Test sorting by created_at (default)
    response = client.get("/task/sortfilter?sort_by=created_at&order=asc", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert tasks[0]["created_at"] <= tasks[1]["created_at"]

    # ✅ Test sorting by priority in descending order
    response = client.get("/task/sortfilter?sort_by=priority&order=desc", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    priority_mapping = {"Low": 1, "Medium": 2, "High": 3}
    task_priorities = [priority_mapping[task["priority"]] for task in tasks]
    assert task_priorities[0] >= task_priorities[1]

    # # ✅ Test invalid sort field
    # response = client.get("/task/sortfilter?sort_by=invalid_field", headers=headers)
    # assert response.status_code == 422  # Unprocessable Entity for invalid field

    # # ✅ Test invalid order field
    # response = client.get("/task/sortfilter?order=invalid_order", headers=headers)
    # assert response.status_code == 422  # Unprocessable Entity for invalid order
