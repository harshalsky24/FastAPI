import pytest
import json
from fastapi.testclient import TestClient
from task.main import app
from task.database import SessionLocal
from task.models import User, Team, Role, TeamMembership, Task
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


def test_remove_member(client, db_session, setup_data):
    """Test adding and removing a member from a team."""
    
    # Get user and team from setup data
    user = setup_data['user']
    team = setup_data['team']
    
    # Generate JWT Token for authentication
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Add the user to the team
    # Prepare request data for adding a team member
    # breakpoint()
    data = {
        "user_id":user.id,
        "role_id":setup_data['role'].id
    }
    team_id = team.id
    headers = {"Authorization": f"Bearer {token}"}

    # Send POST request to add the member
    add_member_response = client.post(f"/team/{team_id}/add-member", 
                                      json=data, headers=headers)
    assert add_member_response.status_code == 200,f"Failed to add member: {add_member_response.json()}"

    # Verify the user was added (You can also verify in the database)
    added_member = db_session.query(TeamMembership).filter_by(user_id=user.id, team_id=team.id).first()
    assert added_member is not None

    # Step 2: Remove the user from the team
    data = {"user_id": user.id}
    headers = {"Authorization": f"Bearer {token}"}

    remove_member_response = client.delete(f"/team/{team_id}/remove-member",data=json.dumps(data),headers=headers)
    assert remove_member_response.status_code == 200, f"Expected 200, got  
    {remove_member_response.status_code}, response: {remove_member_response.text}"
    expected_response = {"message": "User removed from the team successfully"}
    assert remove_member_response.json() == expected_response, f"Expected {expected_response}, got {remove_member_response.json()}"

    # Verify the user was removed (You can also verify in the database)
    removed_member = db_session.query(TeamMembership).filter_by(user_id=user.id, team_id=team.id).first()
    assert removed_member is None

