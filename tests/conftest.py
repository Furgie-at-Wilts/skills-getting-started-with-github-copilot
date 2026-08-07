import pytest
from copy import deepcopy
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Provide a TestClient for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_activities(monkeypatch):
    """Provide isolated activities data for each test
    
    Uses deepcopy to prevent test pollution and monkeypatch to inject
    the fresh data into the app module.
    """
    # Create a fresh copy of activities for this test
    fresh_activities = deepcopy(activities)
    
    # Inject into app module
    monkeypatch.setattr("src.app.activities", fresh_activities)
    
    return fresh_activities
