import pytest
from fastapi.testclient import TestClient
from task.main import app
from task.database import SessionLocal
from task.models import User, Team, Role, TeamMembership
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

@pytest.fixture(scope="function")
def test_role(db_session):
    """Sets up a test role in the database."""
    test_role = Role(role_name="member")
    db_session.add(test_role)
    db_session.commit()
    yield test_role
    db_session.query(Role).filter(Role.role_name == "member").delete()
    db_session.commit()

@pytest.fixture(scope="function")
def test_team(db_session):
    """Sets up a test team in the database."""
    test_team = Team(name="Test Team")
    db_session.add(test_team)
    db_session.commit()
    yield test_team
    db_session.query(Team).filter(Team.name == "Test Team").delete()
    db_session.commit()


def test_remove_team_member_success(db_session, test_user, test_role, test_team):
    """Test removing a team member successfully."""
    # Login to get the authentication token
    valid_credentials = {
        "email": "testuser@example.com",
        "password": "testpassword"
    }
    login_response = client.post("/login", json=valid_credentials)
    token = login_response.json()["access_token"]

    # Prepare request data for adding the team member
    add_member_data = {
        "user_id": test_user.id,
        "role_id": test_role.id
    }
    team_id = test_team.id
    headers = {"Authorization": f"Bearer {token}"}

    add_member_response = client.post(f"/team/{team_id}/add-member", 
                                      json=add_member_data, headers=headers)
    assert add_member_response.status_code == 200,f"Failed to add member: {add_member_response.json()}"


    # Send DELETE request to remove the member
    # remove_member_data = {
    #     "user_id": test_user.id
    # }
    team_id = test_team.id
    print(team_id)
    headers = {"Authorization": f"Bearer {token}"}
    remove_member_response = client.delete(f"/team/{team_id}/remove-member",params={"user_id": test_user.id}, headers=headers)

    # Assertions
    print(remove_member_response.json()) 
    assert remove_member_response.status_code == 200, f"Failed to remove member: {remove_member_response.json()}"
    # response_data = response.json()
    # assert "message" in response_data
    # assert response_data["message"] == "User removed from team successfully."

    # Verify the member is removed from the database
    membership = db_session.query(TeamMembership).filter_by(user_id=test_user.id, team_id=team_id).first()
    assert membership is None, "Membership entry still exists in the database."

    # Cleanup (though the membership should already be removed by the test)
    db_session.commit()
