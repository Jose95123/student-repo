import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def restore_activities():
    """Backup and restore the in-memory activities between tests."""
    original = copy.deepcopy(app_module.activities)
    yield
    # restore original state
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities():
    r = client.get("/activities")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_delete_flow():
    activity = "Chess Club"
    email = "testuser@example.com"

    # Ensure clean start
    r = client.get("/activities")
    assert r.status_code == 200
    assert email not in r.json()[activity]["participants"]

    # Signup
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200
    assert "Signed up" in r.json().get("message", "")

    # Confirm participant is present
    r = client.get("/activities")
    assert email in r.json()[activity]["participants"]

    # Delete participant
    r = client.delete(f"/activities/{activity}/participants", params={"email": email})
    assert r.status_code == 200
    assert "Unregistered" in r.json().get("message", "")

    # Confirm removed
    r = client.get("/activities")
    assert email not in r.json()[activity]["participants"]


def test_double_signup_returns_400():
    activity = "Chess Club"
    email = "double@example.com"

    # First signup should succeed
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 200

    # Second signup should fail with 400
    r = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert r.status_code == 400
