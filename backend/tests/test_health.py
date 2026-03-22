"""Test health and root endpoints."""


def test_health_check(app_client):
    response = app_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root(app_client):
    response = app_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "PANEL"
    assert "docs" in data
