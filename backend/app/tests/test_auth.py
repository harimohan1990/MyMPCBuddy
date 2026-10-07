import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_google_auth_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get Google authorization URL
        url_res = await client.get("/api/v1/auth/google/url")
        assert url_res.status_code == 200
        url_data = url_res.json()
        assert "authorization_url" in url_data
        assert "state" in url_data

        # 2. Google OAuth callback exchange
        cb_res = await client.post("/api/v1/auth/google/callback", json={
            "code": "mock_google_auth_code_test_123",
            "state": url_data["state"]
        })
        assert cb_res.status_code == 200
        cb_data = cb_res.json()
        assert "access_token" in cb_data
        assert "refresh_token" in cb_data

        # 3. Verify user profile with token
        headers = {"Authorization": f"Bearer {cb_data['access_token']}"}
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "hari.mohan@gmail.com"

        # 4. Google One-Tap Sign-In
        one_tap_res = await client.post("/api/v1/auth/google/one-tap", json={
            "email": "hari.mohan@gmail.com",
            "name": "Hari Mohan"
        })
        assert one_tap_res.status_code == 200
        assert "access_token" in one_tap_res.json()
