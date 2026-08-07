import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Test GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        # Arrange
        expected_redirect_url = "/static/index.html"
        
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == expected_redirect_url


class TestGetActivitiesEndpoint:
    """Test GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client, mock_activities):
        # Arrange
        expected_activity_count = len(mock_activities)
        expected_activity_names = list(mock_activities.keys())
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        assert all(name in data for name in expected_activity_names)
    
    def test_get_activities_returns_correct_structure(self, client, mock_activities):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        for activity_name, activity_data in data.items():
            assert all(field in activity_data for field in required_fields)
            assert isinstance(activity_data["participants"], list)
            assert isinstance(activity_data["max_participants"], int)
    
    def test_get_activities_participant_counts_are_correct(self, client, mock_activities):
        # Arrange
        activity_name = "Chess Club"
        expected_participant_count = len(mock_activities[activity_name]["participants"])
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data[activity_name]["participants"]) == expected_participant_count


class TestSignupEndpoint:
    """Test POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_successfully_adds_participant(self, client, mock_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(mock_activities[activity_name]["participants"])
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count + 1
    
    def test_signup_rejects_duplicate_signup(self, client, mock_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_rejects_nonexistent_activity(self, client, mock_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_handles_url_encoded_activity_names(self, client, mock_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "newcoder@mergington.edu"
        
        # Act - FastAPI/TestClient handles URL encoding automatically
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert email in mock_activities[activity_name]["participants"]


class TestUnregisterEndpoint:
    """Test DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_successfully_removes_participant(self, client, mock_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        initial_count = len(mock_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in mock_activities[activity_name]["participants"]
        assert len(mock_activities[activity_name]["participants"]) == initial_count - 1
    
    def test_unregister_rejects_if_not_signed_up(self, client, mock_activities):
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_rejects_nonexistent_activity(self, client, mock_activities):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_updates_participant_count_correctly(self, client, mock_activities):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(mock_activities[activity_name]["participants"])
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert len(mock_activities[activity_name]["participants"]) == initial_count - 1
