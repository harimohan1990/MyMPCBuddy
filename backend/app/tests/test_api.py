import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, Base





@pytest.mark.asyncio
async def test_full_api_workflow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "healthy"

        # 2. Register user
        reg_payload = {
            "email": "hari.mohan@example.com",
            "password": "StrongPassword123!",
            "full_name": "Hari Mohan"
        }
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        token = data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Query current user profile
        me_res = await client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == "hari.mohan@example.com"

        # 4. Check unified notifications inbox
        notif_res = await client.get("/api/v1/notifications", headers=headers)
        assert notif_res.status_code == 200
        inbox_data = notif_res.json()
        assert inbox_data["total"] > 0
        assert len(inbox_data["items"]) > 0

        # Verify items from multiple providers exist in the unified inbox
        providers = {item["provider"] for item in inbox_data["items"]}
        assert "gmail" in providers or "whatsapp" in providers

        # 5. Get notification summary metrics
        summary_res = await client.get("/api/v1/notifications/summary", headers=headers)
        assert summary_res.status_code == 200
        summary = summary_res.json()
        assert summary["total_notifications"] > 0

        # 6. Retrieve daily executive morning briefing
        briefing_res = await client.get("/api/v1/assistant/briefing", headers=headers)
        assert briefing_res.status_code == 200
        briefing = briefing_res.json()
        assert "Hari" in briefing["greeting"]
        assert len(briefing["recommended_priorities"]) > 0

        # 7. Ask AI assistant a question
        query_payload = {"query": "What did Rahul say about the project?"}
        ask_res = await client.post("/api/v1/assistant/query", json=query_payload, headers=headers)
        assert ask_res.status_code == 200
        ask_data = ask_res.json()
        assert len(ask_data["tools_called"]) > 0
        assert "Rahul" in ask_data["answer"] or "project" in ask_data["answer"].lower()

        # 8. Test MCP tool listing
        tools_res = await client.get("/api/v1/mcp/tools", headers=headers)
        assert tools_res.status_code == 200
        tools = tools_res.json()
        tool_names = [t["name"] for t in tools]
        assert "search_messages" in tool_names
        assert "send_email" in tool_names

        # 9. Test MCP WRITE confirmation gate (send_email)
        send_req = {
            "tool_name": "send_email",
            "parameters": {
                "recipient": "colleague@company.com",
                "subject": "Status Update",
                "content": "All systems operational"
            },
            "confirmed": False
        }
        exec_res = await client.post("/api/v1/mcp/execute", json=send_req, headers=headers)
        assert exec_res.status_code == 200
        gate_res = exec_res.json()
        assert gate_res["status"] == "CONFIRMATION_REQUIRED"
        assert gate_res["confirmation_token"] is not None

        # 10. Confirm and execute with valid confirmation token
        confirm_req = {
            "tool_name": "send_email",
            "parameters": {
                "recipient": "colleague@company.com",
                "subject": "Status Update",
                "content": "All systems operational"
            },
            "confirmed": True,
            "confirmation_token": gate_res["confirmation_token"]
        }
        dispatched_res = await client.post("/api/v1/mcp/execute", json=confirm_req, headers=headers)
        assert dispatched_res.status_code == 200
        assert dispatched_res.json()["status"] == "EXECUTED"

        # 11. Verify privacy center telemetry
        privacy_res = await client.get("/api/v1/privacy/stats", headers=headers)
        assert privacy_res.status_code == 200
        assert privacy_res.json()["token_encryption"] == "AES-256-GCM (Authenticated at rest)"
