from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.mcp import MCPToolSchema, ToolExecutionRequest, ToolExecutionResponse
from app.mcp.server import MCPServer
from app.api.deps import get_current_user

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])


@router.get("/tools", response_model=List[MCPToolSchema])
async def list_tools(current_user: User = Depends(get_current_user)):
    return MCPServer.get_registered_tools()


@router.post("/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    req: ToolExecutionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    client_ip = request.client.host if request.client else "unknown"
    return await MCPServer.execute_tool(
        db=db,
        user_id=current_user.id,
        tool_name=req.tool_name,
        parameters=req.parameters,
        confirmed=req.confirmed,
        confirmation_token=req.confirmation_token,
        client_ip=client_ip
    )
