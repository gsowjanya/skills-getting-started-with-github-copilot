"""
Test suite for the Mergington High School Activities API

This module contains comprehensive tests for all API endpoints using the
Arrange-Act-Assert (AAA) testing pattern.
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Fixture to provide a TestClient instance for the FastAPI app"""
    return TestClient(app)


class TestGetActivities:
    """Test cases for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities"""
        # Arrange
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Club",
            "Soccer Team",
            "Drama Club",
            "Visual Arts",
            "Debate Club",
            "Science Club"
        ]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_response_structure(self, client):
        """Test that each activity has the required fields"""
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data, dict)
            assert required_fields.issubset(set(activity_data.keys()))
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)


class TestSignupForActivity:
    """Test cases for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_success(self, client):
        """Test successfully signing up a new student for an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert email in result["message"]
        assert activity_name in result["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that a student is added to the activity's participants list"""
        # Arrange
        activity_name = "Programming Class"
        email = "alice@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_duplicate_student_returns_400(self, client):
        """Test that signing up a student already registered returns 400"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"].lower()

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test that signing up for a non-existent activity returns 404"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"].lower()

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple students can sign up for the same activity"""
        # Arrange
        activity_name = "Drama Club"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email1}")
        client.post(f"/activities/{activity_name}/signup?email={email2}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email1 in activities[activity_name]["participants"]
        assert email2 in activities[activity_name]["participants"]

    def test_signup_same_student_multiple_activities(self, client):
        """Test that the same student can sign up for multiple activities"""
        # Arrange
        email = "versatile@mergington.edu"
        activities = ["Chess Club", "Drama Club"]

        # Act
        for activity in activities:
            client.post(f"/activities/{activity}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities_data = response.json()
        for activity in activities:
            assert email in activities_data[activity]["participants"]


class TestRootEndpoint:
    """Test cases for GET / endpoint"""

    def test_root_endpoint_redirects(self, client):
        """Test that GET / redirects to /static/index.html"""
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_endpoint_follow_redirect(self, client):
        """Test following the redirect from / to /static/index.html"""
        # Arrange
        # Act
        response = client.get("/", follow_redirects=True)

        # Assert
        assert response.status_code == 200
