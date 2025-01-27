import unittest
from fastapi.testclient import TestClient
from task.main import app
from task.auth import create_access_token
from task.database import SessionLocal
from task.models import Team, User
from task.hashing import get_password_hash


client = TestClient(app)

class TestTeamCreat(unittest.TestCase):
    def setUp(self):
        db = SessionLocal()
        test_user = User(
            username="testuser",
            email="testuser@example.com",
            hashed_password=get_password_hash("testpassword")
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        db.close()
        self.token = create_access_token({"sub":test_user.id})
        self.headers = {"Authorization":f"bearer{self.token}"}

        print(self.token)
        print(self.headers)

    def test_create_team_success(self):
        response = client.post("/team-create", json={"name": "Test Team"}, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "Team created successfully")
        self.assertEqual(response.json()["team"]["name"],"Test Team")

    def test_create_existing_team(self):
        db = SessionLocal()
        db.add(Team(name = "Existing Team"))
        db.commit()
        db.close()

        response = client.post("/team-create",json = "Existing Team", headers = self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"],"Team with this name already exist")

    def tearDown(self):
        db = SessionLocal()
        db.query(Team).filter(Team.name == "Test Team").delete()
        db.commit()
        db.close()

if __name__ == "main":
    unittest.main()

