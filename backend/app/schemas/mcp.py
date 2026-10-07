from pydantic import BaseModel
from typing import Dict, Any, Optional, List


class MCPToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class MCPToolSchema(BaseModel):
    name: str
    description: str
    permission_level: str  # "READ", "WRITE", "DESTRUCTIVE"
    requires_confirmation: bool
    provider: str
    parameters: List[MCPToolParameter]


class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any] = {}
    confirmed: bool = False
    confirmation_token: Optional[str] = None


class ToolExecutionResponse(BaseModel):
    status: str  # "EXECUTED", "CONFIRMATION_REQUIRED", "FAILED"
    tool_name: str
    result: Optional[Any] = None
    confirmation_token: Optional[str] = None
    confirmation_prompt: Optional[str] = None
    error: Optional[str] = None
