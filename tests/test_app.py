import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial activities data for resetting
initial_activities = {
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
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Fridays, 3:00 PM - 4:30 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other art forms",
        "schedule": "Mondays, 3:00 PM - 4:30 PM",
        "max_participants": 10,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and learn theater skills",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 12,
        "participants": []
    },
    "Debate Club": {
        "description": "Practice debating and public speaking",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 8,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and learn about science",
        "schedule": "Mondays and Fridays, 3:00 PM - 4:00 PM",
        "max_participants": 15,
        "participants": []
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the global activities dict to initial state before each test."""
    activities.clear()
    activities.update(initial_activities)

client = TestClient(app)

def test_get_activities():
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert len(data["Chess Club"]["participants"]) == 2

def test_root_redirect():
    """Test root endpoint redirects to static file."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_signup_happy_path():
    """Test successful signup."""
    response = client.post("/activities/Basketball Team/signup?email=newstudent@mergington.edu")
    assert response.status_code == 200
    assert "Signed up newstudent@mergington.edu for Basketball Team" in response.json()["message"]
    assert "newstudent@mergington.edu" in activities["Basketball Team"]["participants"]

def test_signup_activity_not_found():
    """Test signup for non-existent activity."""
    response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_already_signed_up():
    """Test duplicate signup."""
    client.post("/activities/Basketball Team/signup?email=duplicate@mergington.edu")
    response = client.post("/activities/Basketball Team/signup?email=duplicate@mergington.edu")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"

def test_unregister_happy_path():
    """Test successful unregister."""
    client.post("/activities/Basketball Team/signup?email=remove@mergington.edu")
    response = client.delete("/activities/Basketball Team/unregister?email=remove@mergington.edu")
    assert response.status_code == 200
    assert "Unregistered remove@mergington.edu from Basketball Team" in response.json()["message"]
    assert "remove@mergington.edu" not in activities["Basketball Team"]["participants"]

def test_unregister_activity_not_found():
    """Test unregister from non-existent activity."""
    response = client.delete("/activities/Nonexistent Activity/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_participant_not_found():
    """Test unregister when not signed up."""
    response = client.delete("/activities/Basketball Team/unregister?email=notsigned@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"