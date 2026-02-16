import copy

from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


# Preserve original activities to reset between tests
_ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_ORIGINAL_ACTIVITIES))


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_duplicate():
    client = TestClient(app)
    activity = "Chess Club"
    email = "tester@example.com"

    # First signup should succeed
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Duplicate signup should return 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister():
    client = TestClient(app)
    activity = "Programming Class"
    email = "temp_user@example.com"

    # Sign up then unregister
    r = client.post(f"/activities/{activity}/signup?email={email}")
    assert r.status_code == 200

    r2 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r2.status_code == 200
    assert "Unregistered" in r2.json().get("message", "")

    # Unregistering again should return 400
    r3 = client.delete(f"/activities/{activity}/participants?email={email}")
    assert r3.status_code == 400


def test_nonexistent_activity():
    client = TestClient(app)
    r = client.post("/activities/Nope/signup?email=a@b.com")
    assert r.status_code == 404
    r2 = client.delete("/activities/Nope/participants?email=a@b.com")
    assert r2.status_code == 404
