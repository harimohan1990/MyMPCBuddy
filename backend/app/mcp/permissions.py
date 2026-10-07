import hmac
import hashlib
import json
import time
from typing import Dict, Any, Tuple
from enum import Enum
from app.core.config import settings


class PermissionLevel(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    DESTRUCTIVE = "DESTRUCTIVE"


class MCPPermissionManager:
    """
    Manages tool permissions and enforces cryptographic confirmation tokens
    for WRITE and DESTRUCTIVE tool executions.
    """

    @staticmethod
    def requires_confirmation(level: PermissionLevel) -> bool:
        return level in (PermissionLevel.WRITE, PermissionLevel.DESTRUCTIVE)

    @staticmethod
    def generate_confirmation_token(tool_name: str, user_id: str, parameters: Dict[str, Any], ttl_seconds: int = 300) -> str:
        """
        Generates an HMAC-SHA256 signature containing the tool call details and expiration timestamp.
        """
        payload = {
            "tool_name": tool_name,
            "user_id": user_id,
            "params_hash": hashlib.sha256(json.dumps(parameters, sort_keys=True).encode()).hexdigest(),
            "expires_at": int(time.time()) + ttl_seconds
        }
        serialized = json.dumps(payload, sort_keys=True)
        signature = hmac.new(settings.SECRET_KEY.encode(), serialized.encode(), hashlib.sha256).hexdigest()
        import base64
        token_data = {"data": payload, "sig": signature}
        return base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()

    @staticmethod
    def verify_confirmation_token(token: str, tool_name: str, user_id: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        import base64
        try:
            raw = base64.urlsafe_b64decode(token.encode()).decode()
            token_obj = json.loads(raw)
            payload = token_obj.get("data", {})
            signature = token_obj.get("sig", "")

            # Verify signature
            serialized = json.dumps(payload, sort_keys=True)
            expected_sig = hmac.new(settings.SECRET_KEY.encode(), serialized.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_sig):
                return False, "Invalid cryptographic token signature"

            # Check expiration
            if time.time() > payload.get("expires_at", 0):
                return False, "Confirmation token has expired"

            # Check tool and user binding
            if payload.get("tool_name") != tool_name:
                return False, "Token was issued for a different tool"

            if payload.get("user_id") != user_id:
                return False, "Token was issued for a different user"

            # Check parameters hash
            current_params_hash = hashlib.sha256(json.dumps(parameters, sort_keys=True).encode()).hexdigest()
            if payload.get("params_hash") != current_params_hash:
                return False, "Parameters modified after confirmation was requested"

            return True, "Valid"
        except Exception as e:
            return False, f"Malformed token: {str(e)}"
