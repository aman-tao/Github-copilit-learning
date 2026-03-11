"""
FastAPI tests using AAA (Arrange-Act-Assert) pattern
Tests for High School Activities Management System
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Fixture that provides a fresh TestClient with clean activity data for each test.
    
    Arrange: Initializes test data by resetting the global activities dictionary
    """
    # Arrange: Set up fresh test data
    fresh_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": []
        }
    }
    
    # Replace the app's activities with fresh data
    activities.clear()
    activities.update(fresh_activities)
    
    yield TestClient(app)
    
    # Cleanup after test
    activities.clear()


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_all_activities(self, client):
        """Should return all activities with correct structure"""
        # Arrange: Test data already set up by fixture
        
        # Act: Make request to get all activities
        response = client.get("/activities")
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    
    def test_activity_has_required_fields(self, client):
        """Should include all required fields for each activity"""
        # Arrange: Test data already set up by fixture
        
        # Act: Get activities
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Check required fields exist
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_success(self, client):
        """Should successfully sign up a new student for an activity"""
        # Arrange: Prepare test data
        activity_name = "Programming Class"
        email = "newstudent@mergington.edu"
        
        # Act: Sign up for activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify successful response and data updated
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        
        # Verify participant was added
        activities_response = client.get("/activities").json()
        assert email in activities_response[activity_name]["participants"]
    
    def test_signup_duplicate_student_returns_error(self, client):
        """Should reject signup if student is already registered"""
        # Arrange: Student already in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Try to sign up again
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    
    def test_signup_nonexistent_activity_returns_not_found(self, client):
        """Should return 404 if activity does not exist"""
        # Arrange: Prepare non-existent activity name
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act: Try to sign up for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client):
        """Should successfully unregister a participant from an activity"""
        # Arrange: Student is in Chess Club
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act: Unregister from activity
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert: Verify successful response
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        
        # Verify participant was removed
        activities_response = client.get("/activities").json()
        assert email not in activities_response[activity_name]["participants"]
    
    def test_unregister_nonexistent_participant_returns_error(self, client):
        """Should return 400 if participant is not registered"""
        # Arrange: Student not in Programming Class
        activity_name = "Programming Class"
        email = "notregistered@mergington.edu"
        
        # Act: Try to unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert: Verify error response
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"
    
    def test_unregister_from_nonexistent_activity_returns_not_found(self, client):
        """Should return 404 if activity does not exist"""
        # Arrange: Prepare non-existent activity
        activity_name = "NonExistent Club"
        email = "student@mergington.edu"
        
        # Act: Try to unregister from non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert: Verify 404 response
        assert response.status_code == 404
        assert response.json()["detail"] == "Activity not found"


class TestRedirect:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """Should redirect root path to /static/index.html"""
        # Arrange: Test root endpoint (no additional setup needed)
        
        # Act: Make request to root
        response = client.get("/", follow_redirects=False)
        
        # Assert: Verify redirect response
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
