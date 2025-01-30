import pytest
import json
from fastapi.testclient import TestClient
from task.main import app
from task.database import SessionLocal
from task.models import User, Team, Role, TeamMembership
from task.hashing import get_password_hash
from task.auth import create_access_token

client = TestClient(app)

@pytest.fixture(scope="module")
def client():
    """Provides a TestClient for FastAPI."""
    return TestClient(app)

@pytest.fixture(scope="function")
def db_session():
    """Provides a fresh database session for each test."""
    db = SessionLocal()
    yield db
    db.rollback()  # Ensures a clean state for each test
    db.close()

@pytest.fixture(scope="function")
def setup_data(db_session, client):
    """Setup test data: User, Team, Role before running the test."""
    
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

    # Generate JWT Token for authentication
    token = create_access_token({"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    yield {
        "user": test_user,
        "team": test_team,
        "role": test_role,
        "headers": headers
    }

    # Cleanup: Remove all test data
    db_session.query(TeamMembership).filter_by(team_id=test_team.id).delete()
    db_session.query(Role).filter_by(id=test_role.id).delete()
    db_session.query(Team).filter_by(id=test_team.id).delete()
    db_session.query(User).filter_by(id=test_user.id).delete()
    db_session.commit()


def test_remove_member(client, db_session, setup_data):
    """Test adding and removing a member from a team using API calls."""
    
    # Get user and team from setup data
    user = setup_data['user']
    team = setup_data['team']
    role = setup_data['role']
    headers = setup_data['headers']

    # Step 1: Add the user to the team via API
    data = {
        "user_id": user.id,
        "role_id": role.id
    }
    team_id = team.id

    add_member_response = client.post(f"/team/{team_id}/add-member", json=data, headers=headers)
    assert add_member_response.status_code == 200, f"Failed to add member: {add_member_response.json()}"

    # Verify the user was added
    added_member = db_session.query(TeamMembership).filter_by(user_id=user.id, team_id=team.id).first()
    assert added_member is not None

    # Step 2: Remove the user from the team via API
    remove_data = {"user_id": user.id}
    remove_member_response = client.request(method="DELETE",url=f"/team/{team_id}/remove-member",
                                            headers=headers,json=remove_data )

    assert remove_member_response.status_code == 200, f"Expected 200, got {remove_member_response.status_code}, response: {remove_member_response.text}"
    expected_response = {"message": "User Deleted from the team successfully"}
    assert remove_member_response.json() == expected_response, f"Expected {expected_response}, got {remove_member_response.json()}"

    # Verify the user was removed from the database
    removed_member = db_session.query(TeamMembership).filter_by(user_id=user.id, team_id=team.id).first()
    assert removed_member is None
