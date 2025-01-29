import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from task.main import app
from task.database import get_db, SessionLocal
from task.models import User, Team, Task, Role, TeamMembership
from task.hashing import get_password_hash
from datetime import datetime
from task.auth import create_access_token
from fastapi import HTTPException, status


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

    # Assign a role (admin for test_admin_user)
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

def create_test_task(db_session: Session, user: User, team: Team, status="In Progress"):
    """Helper function to create a test task."""
    task = Task(
        title="Test Task",
        description="This is a test task",
        status=status,
        priority="High",
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


# Test case: Valid Team Dashboard Access
def test_team_dashboard_valid_access(client, db_session, setup_data):
    """Test the team dashboard for a valid user who is a member of the team."""

    # Get user and team from setup data
    user = setup_data['user']
    team = setup_data['team']

    # Create a test task and assign it to the user
    create_test_task(db_session, user, team, status="In Progress")
    create_test_task(db_session, user, team, status="In Review")
    
    # Generate JWT Token for authentication
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Test the team dashboard
    response = client.get(f"/dashboard/team-dashboard/{team.id}", headers=headers)
    assert response.status_code == 200

    dashboard_data = response.json()

    # Check if the response includes assigned tasks
    assert "all_assigned_task" in dashboard_data
    assert "in_process_tasks" in dashboard_data
    assert "awaiting_assigned_tasks" in dashboard_data

    # Check the number of tasks in each category
    assert len(dashboard_data["all_assigned_task"]) > 0
    assert len(dashboard_data["in_process_tasks"]) > 0
    assert len(dashboard_data["awaiting_assigned_tasks"]) > 0


# Test case: Invalid Team
def test_team_dashboard_invalid_team(client, db_session, setup_data):
    """Test the team dashboard with an invalid team ID (non-existent team)."""

    # Generate JWT Token for authentication as admin user
    user = setup_data['user']
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Test the team dashboard with a non-existent team
    response = client.get("/dashboard/team-dashboard/9999", headers=headers)
    assert response.status_code == 404
    assert response.json() == {"detail": "Team not found"}


# Test case: User Not a Member of the Team
def test_team_dashboard_non_member_access(client, db_session, setup_data):
    """Test the team dashboard for a user who is not a member of the team."""

    # Create a non-member user
    non_member_user = User(
        username="nonmemberuser",
        email="nonmemberuser@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(non_member_user)
    db_session.commit()
    db_session.refresh(non_member_user)

    # Generate JWT Token for authentication as non-member user
    token = create_access_token({"sub": str(non_member_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Test the team dashboard for a non-member user
    response = client.get(f"/dashboard/team-dashboard/{setup_data['team'].id}", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "You are not a member of this team"}

    # Cleanup non-member user
    db_session.query(TeamMembership).filter_by(user_id=non_member_user.id).delete()
    db_session.query(User).filter_by(id=non_member_user.id).delete()
    db_session.commit()
