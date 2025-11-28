"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store the original activities
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and varsity play",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and participate in friendly matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["chris@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in theatrical productions and develop acting skills",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["maya@mergington.edu", "james@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu"]
        },
        "Robotics Club": {
            "description": "Design and build robots for competitions",
            "schedule": "Mondays and Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["liam@mergington.edu", "noah@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and experiments",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu"]
        }
    }
    
    # Clear and repopulate activities
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Reset again after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_includes_activity_details(self, client):
        """Test that activities include all required fields"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
    
    def test_get_activities_includes_participants(self, client):
        """Test that activities include participant list"""
        response = client.get("/activities")
        data = response.json()
        chess_club = data["Chess Club"]
        
        assert len(chess_club["participants"]) == 2
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successful(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "newstudent@mergington.edu" in chess_club["participants"]
    
    def test_signup_duplicate_student(self, client):
        """Test that a student cannot sign up twice"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/Fake%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up"""
        # First signup
        response1 = client.post(
            "/activities/Tennis%20Club/signup?email=student1@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(
            "/activities/Tennis%20Club/signup?email=student2@mergington.edu"
        )
        assert response2.status_code == 200
        
        # Verify both are added
        activities_response = client.get("/activities")
        tennis_club = activities_response.json()["Tennis Club"]
        assert "student1@mergington.edu" in tennis_club["participants"]
        assert "student2@mergington.edu" in tennis_club["participants"]
        assert len(tennis_club["participants"]) == 3


class TestUnregister:
    """Test the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successful(self, client):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess_club["participants"]
    
    def test_unregister_not_registered(self, client):
        """Test unregistering a student who is not registered"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_nonexistent_activity(self, client):
        """Test unregistering from a non-existent activity"""
        response = client.post(
            "/activities/Fake%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_unregister_multiple_participants(self, client):
        """Test unregistering one participant doesn't affect others"""
        # Unregister first participant
        response1 = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response1.status_code == 200
        
        # Verify second participant is still there
        activities_response = client.get("/activities")
        chess_club = activities_response.json()["Chess Club"]
        assert "michael@mergington.edu" not in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]
        assert len(chess_club["participants"]) == 1


class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_signup_and_unregister_workflow(self, client):
        """Test a complete signup and unregister workflow"""
        email = "workflow@mergington.edu"
        activity = "Programming%20Class"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Programming Class"]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        after_signup_count = len(response.json()["Programming Class"]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        final_count = len(response.json()["Programming Class"]["participants"])
        assert final_count == initial_count
    
    def test_availability_calculation(self, client):
        """Test that availability spots are calculated correctly"""
        response = client.get("/activities")
        data = response.json()
        
        # Chess Club: max 12, has 2 participants, should have 10 spots left
        chess_club = data["Chess Club"]
        spots_left = chess_club["max_participants"] - len(chess_club["participants"])
        assert spots_left == 10
        
        # Gym Class: max 30, has 2 participants, should have 28 spots left
        gym_class = data["Gym Class"]
        spots_left = gym_class["max_participants"] - len(gym_class["participants"])
        assert spots_left == 28
