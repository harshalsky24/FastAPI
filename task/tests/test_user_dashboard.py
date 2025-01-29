import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from task.main import app
from task.database import get_db, SessionLocal
from task.models import User, Team, Task, Role, TeamMembership
from task.hashing import get_password_hash
from datetime import datetime
from task.auth import create_access_token

# Test fixtures
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

# Test case
def test_user_dashboard(client, db_session, setup_data):
    """Test the user dashboard API with authentication."""

    # Get user and team from setup data
    user = setup_data['user']
    team = setup_data['team']

    # Generate JWT Token for authentication
    token = create_access_token({"sub": str(user.id)}) 
    headers = {"Authorization": f"Bearer {token}"}

    # Create test tasks: assigned, created, and review tasks
    assigned_task = create_test_task(db_session, user, team, status="In Progress", priority="High")
    created_task = create_test_task(db_session, user, team, status="Completed", priority="Medium")
    review_task = create_test_task(db_session, user, team, status="In Review", priority="Low")

    # ✅ Test the user dashboard
    response = client.get("/dashboard/user-dashboard", headers=headers)
    assert response.status_code == 200

    dashboard_data = response.json()

    # Check if the user ID and username are correct
    assert dashboard_data["user_id"] == user.id
    assert dashboard_data["user_name"] == user.username

    # Check the assigned, created, and review tasks are returned correctly
    assigned_task_ids = [task["id"] for task in dashboard_data["assigned_tasks"]]
    created_task_ids = [task["id"] for task in dashboard_data["created_tasks"]]
    review_task_ids = [task["id"] for task in dashboard_data["review_tasks"]]

    # Assert that the tasks are correctly assigned, created, and reviewed
    assert assigned_task.id in assigned_task_ids
    assert created_task.id in created_task_ids
    assert review_task.id in review_task_ids

     # Check that the task lists are empty as no tasks were created
    # assert dashboard_data["assigned_tasks"] == []
    # assert dashboard_data["created_tasks"] == []
    # assert dashboard_data["review_tasks"] == []
