import pytest
from app.mcp.permissions import MCPPermissionManager, PermissionLevel


def test_permission_level_check():
    assert MCPPermissionManager.requires_confirmation(PermissionLevel.READ) is False
    assert MCPPermissionManager.requires_confirmation(PermissionLevel.WRITE) is True
    assert MCPPermissionManager.requires_confirmation(PermissionLevel.DESTRUCTIVE) is True


def test_confirmation_token_validation():
    user_id = "user-abc-123"
    tool_name = "send_email"
    params = {"recipient": "boss@company.com", "subject": "Update", "content": "Done"}

    # Generate token
    token = MCPPermissionManager.generate_confirmation_token(tool_name, user_id, params)
    assert token is not None

    # Verify with identical parameters
    valid, msg = MCPPermissionManager.verify_confirmation_token(token, tool_name, user_id, params)
    assert valid is True
    assert msg == "Valid"

    # Verify with tampered parameters
    tampered_params = {"recipient": "attacker@evil.com", "subject": "Update", "content": "Done"}
    tampered_valid, reason = MCPPermissionManager.verify_confirmation_token(token, tool_name, user_id, tampered_params)
    assert tampered_valid is False
    assert "Parameters modified" in reason
