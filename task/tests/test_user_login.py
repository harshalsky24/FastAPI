import unittest
from fastapi.testclient import TestClient
from task.main import app
from task.database import get_db, SessionLocal
from task.models import User
from task.hashing import get_password_hash

client = TestClient(app)

class TestUserLogin(unittest.TestCase):

    def setUp(self):
        """Set up a test user in the database before running the test."""
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

    def tearDown(self):
        """Clean up the test user after the test is done."""
        db = SessionLocal()
        db.query(User).filter(User.username == "testuser").delete()
        db.commit()
        db.close()

    def test_login_user(self):
        """Test the login endpoint with valid and invalid credentials."""

        valid_credentials = {
            "email": "testuser@example.com",
            "password": "testpassword"
        }
        response = client.post("/login", json=valid_credentials)
        print("Valid Login - Status Code:", response.status_code)
        print("Valid Login - Response JSON:", response.json())

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")

        # Test invalid login (wrong password)
        invalid_credentials = {
            "email": "testuser@example.com",
            "password": "wrongpassword"
        }
        response = client.post("/login", json=invalid_credentials)
        print("Invalid Login - Status Code:", response.status_code)
        print("Invalid Login - Response JSON:", response.json())

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

        # Test invalid login (non-existent email)
        non_existent_user = {
            "email": "wronguser@example.com",
            "password": "testpassword"
        }
        response = client.post("/login", json=non_existent_user)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

if __name__ == "__main__":
    unittest.main()
