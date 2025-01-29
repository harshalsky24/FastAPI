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

def create_test_task(db_session: Session, user: User, team: Team):
    """Helper function to create a test task."""
    task = Task(
        title="Test Task",
        description="This is a test task",
        status="In Progress",
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

# Test case
def test_admin_dashboard_valid_access(client, db_session, setup_data):
    """Test the admin dashboard API for an admin user."""

    # Get user and team from setup data
    user = setup_data['user']
    team = setup_data['team']

    # Create a test task for the admin
    create_test_task(db_session, user, team)

    # Generate JWT Token for authentication as admin
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Test the admin dashboard
    response = client.get("/dashboard/admin-dashboard", headers=headers)
    assert response.status_code == 200

    dashboard_data = response.json()

    # Check if the response includes total counts
    assert "total_counts" in dashboard_data
    assert "total_tasks" in dashboard_data["total_counts"]
    assert "total_users" in dashboard_data["total_counts"]
    assert "total_team" in dashboard_data["total_counts"]

    # Check if the response includes the recent data
    assert "all_data" in dashboard_data
    assert "Tasks" in dashboard_data["all_data"]
    assert "users" in dashboard_data["all_data"]
    assert "teams" in dashboard_data["all_data"]

    # Check that the correct number of recent tasks, users, and teams are returned
    assert len(dashboard_data["all_data"]["Tasks"]) > 0
    assert len(dashboard_data["all_data"]["users"]) > 0
    assert len(dashboard_data["all_data"]["teams"]) > 0


def test_admin_dashboard_invalid_access(client, db_session, setup_data):
    """Test the admin dashboard API for a non-admin user (should return 403)."""

    # Create a non-admin user
    non_admin_user = User(
        username="nonadminuser",
        email="nonadminuser@example.com",
        hashed_password=get_password_hash("testpassword")
    )
    db_session.add(non_admin_user)
    db_session.commit()
    db_session.refresh(non_admin_user)

    # Assign a non-admin role to the new user
    non_admin_role = Role(role_name="member")
    db_session.add(non_admin_role)
    db_session.commit()
    db_session.refresh(non_admin_role)

    # Add user to a team with a non-admin role
    non_admin_team_membership = TeamMembership(
        team_id=setup_data["team"].id,
        user_id=non_admin_user.id,
        role_id=non_admin_role.id
    )
    db_session.add(non_admin_team_membership)
    db_session.commit()

    # Generate JWT Token for authentication as non-admin user
    token = create_access_token({"sub": str(non_admin_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Test the admin dashboard with non-admin user
    response = client.get("/dashboard/admin-dashboard", headers=headers)
    assert response.status_code == 403
    assert response.json() == {"detail": "you do not have permission to access."}

    # Cleanup non-admin user
    db_session.query(TeamMembership).filter_by(user_id=non_admin_user.id).delete()
    db_session.query(Role).filter_by(id=non_admin_role.id).delete()
    db_session.query(User).filter_by(id=non_admin_user.id).delete()
    db_session.commit()
