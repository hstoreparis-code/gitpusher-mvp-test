import pytest
from fastapi.testclient import TestClient

from server import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_e2e_push_credits_ok(monkeypatch):
    # We mock the underlying pipeline by patching complete_job to simulate success
    from services.credits_service import CreditsService

    async def fake_consume_credits(self, user_id: str, amount: int = 1) -> bool:
        # pretend everything is fine without touching real DB
        return True

    monkeypatch.setattr(CreditsService, "consume_credits", fake_consume_credits)

    # Just call /push and ensure it returns 200 and a success status
    resp = client.post("/push", json={
        "provider": "github",
        "source": "code",
        "repo_name": "test-repo",
        "content": {"files": []},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "repo_url" in data
