import copy

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    original_data = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_data)


@pytest.fixture()
def client():
    return TestClient(app)


def test_get_activities(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert expected_activity in data
    assert data[expected_activity]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_success(client):
    # Arrange
    signup_url = "/activities/Chess Club/signup?email=test@mergington.edu"
    expected_email = "test@mergington.edu"
    expected_activity = "Chess Club"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Signed up {expected_email} for {expected_activity}"}
    assert expected_email in activities[expected_activity]["participants"]


def test_signup_for_activity_duplicate_fails(client):
    # Arrange
    signup_url = "/activities/Chess Club/signup?email=michael@mergington.edu"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student alrealdy sign up!"


def test_remove_participant_success(client):
    # Arrange
    delete_url = "/activities/Chess Club/participants?email=michael@mergington.edu"
    expected_activity = "Chess Club"
    expected_email = "michael@mergington.edu"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": f"Removed {expected_email} from {expected_activity}"}
    assert expected_email not in activities[expected_activity]["participants"]


def test_remove_missing_participant_returns_404(client):
    # Arrange
    delete_url = "/activities/Chess Club/participants?email=notfound@mergington.edu"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Participant not found"
