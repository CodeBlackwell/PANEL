"""Test session management endpoints."""


def test_list_agents(app_client):
    response = app_client.get("/api/v1/sessions")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert len(agents) == 13
    # Check default agents are present
    ids = [a["id"] for a in agents]
    assert "architect" in ids
    assert "security" in ids


def test_create_session(app_client):
    response = app_client.post("/api/v1/sessions")
    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["phase"] == "created"


def test_get_session(app_client):
    # Create first
    create_resp = app_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    # Get
    response = app_client.get(f"/api/v1/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["id"] == session_id
    assert response.json()["phase"] == "created"


def test_get_session_not_found(app_client):
    response = app_client.get("/api/v1/sessions/nonexistent-id")
    assert response.status_code == 404


def test_submit_idea(app_client):
    # Create session
    create_resp = app_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    # Submit idea
    response = app_client.post(
        f"/api/v1/sessions/{session_id}/idea",
        json={"idea": "Build a todo app with real-time sync"},
    )
    assert response.status_code == 200
    assert response.json()["phase"] == "idea_submitted"


def test_submit_idea_too_short(app_client):
    create_resp = app_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]

    response = app_client.post(
        f"/api/v1/sessions/{session_id}/idea",
        json={"idea": "short"},
    )
    assert response.status_code == 422  # Validation error


def test_configure_session(app_client):
    # Create + submit idea
    create_resp = app_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]
    app_client.post(
        f"/api/v1/sessions/{session_id}/idea",
        json={"idea": "Build a todo app with real-time sync"},
    )

    # Configure
    response = app_client.post(
        f"/api/v1/sessions/{session_id}/config",
        json={
            "selected_agents": ["architect", "security", "devops"],
            "debate_rounds": 5,
        },
    )
    assert response.status_code == 200
    assert response.json()["phase"] == "configured"


def test_configure_too_few_agents(app_client):
    create_resp = app_client.post("/api/v1/sessions")
    session_id = create_resp.json()["session_id"]
    app_client.post(
        f"/api/v1/sessions/{session_id}/idea",
        json={"idea": "Build a todo app with real-time sync"},
    )

    response = app_client.post(
        f"/api/v1/sessions/{session_id}/config",
        json={"selected_agents": ["architect"], "debate_rounds": 5},
    )
    assert response.status_code == 422  # Validation error (min_length=2)
