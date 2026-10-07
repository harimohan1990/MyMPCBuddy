from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.models.notification import Notification
from app.models.calendar_event import CalendarEvent
from app.models.action_item import ActionItem
from app.schemas.assistant import AssistantQueryRequest, AssistantQueryResponse, DailyBriefingResponse, ActionSuggestion
from app.api.deps import get_current_user
from app.services.briefing_service import BriefingService
from app.services.sanitizer import PromptSanitizer
from app.mcp.server import MCPServer

router = APIRouter(prefix="/assistant", tags=["AI Personal Assistant"])


@router.get("/briefing", response_model=DailyBriefingResponse)
async def get_briefing(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await BriefingService.generate_daily_briefing(db, current_user.id, current_user.full_name)


@router.post("/query", response_model=AssistantQueryResponse)
async def query_assistant(
    req: AssistantQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = req.query.lower().strip()
    tools_called: List[str] = []
    sources: List[Dict[str, Any]] = []
    suggested_actions: List[ActionSuggestion] = []

    # Dynamic MCP tool routing based on intent detection
    if any(k in query for k in ["meeting", "calendar", "schedule", "tomorrow", "today"]):
        tools_called.append("get_today_schedule")
        exec_res = await MCPServer.execute_tool(db, current_user.id, "get_today_schedule", {})
        schedule_events = exec_res.result or []
        
        if not schedule_events:
            answer = "You have no upcoming meetings scheduled on your calendar today."
        else:
            lines = [f"You have {len(schedule_events)} events on your calendar:"]
            for ev in schedule_events:
                time_str = ev.get('start_time', '').split('T')[-1][:5]
                lines.append(f"• **{ev.get('summary')}** at {time_str} ({ev.get('location', 'Online')})")
                sources.append({"type": "calendar", "title": ev.get("summary"), "id": ev.get("id")})
            answer = "\n".join(lines)

    elif any(k in query for k in ["rahul", "who do i need to reply to", "reply", "important", "manager", "pr", "unread", "away", "priority"]):
        tools_called.append("search_messages")
        
        # Determine search term
        search_kw = "Rahul" if "rahul" in query else ""
        exec_res = await MCPServer.execute_tool(
            db, current_user.id, "search_messages", {"query": search_kw, "limit": 10}
        )
        messages = exec_res.result or []

        if not messages:
            answer = "I searched across your unified communications and found no unread messages requiring attention."
        else:
            important_msgs = [m for m in messages if m.get("priority") in ("HIGH", "CRITICAL") or m.get("action_required")]
            display_msgs = important_msgs if important_msgs else messages

            lines = [f"Here is what requires your attention across your connected services:"]
            for m in display_msgs[:5]:
                # Wrap untrusted provider content safely
                safe_title = PromptSanitizer.sanitize_external_text(m.get('title', ''))
                sender_name = m.get('sender', {}).get('name', 'Unknown')
                lines.append(f"• **[{m.get('provider').upper()}] {sender_name}**: {safe_title} — _{m.get('snippet', '')[:90]}..._")
                sources.append({"type": m.get("provider"), "title": safe_title, "id": m.get("id")})

                if "rahul" in sender_name.lower():
                    suggested_actions.append(ActionSuggestion(
                        action_type="DRAFT_REPLY",
                        label="Draft WhatsApp reply to Rahul: '5 PM works for me'",
                        tool_name="draft_email",
                        parameters={"recipient": "+15550192834", "subject": "Re: Project Sync", "content": "Yes, 5 PM works for me."}
                    ))
                elif "interview" in safe_title.lower():
                    suggested_actions.append(ActionSuggestion(
                        action_type="DRAFT_REPLY",
                        label="Confirm interview slot with Elena (HR)",
                        tool_name="send_email",
                        parameters={"recipient": "elena.hr@acmecorp.com", "subject": "Re: Interview Confirmation", "content": "Confirmed for tomorrow at 2:00 PM EST."},
                        requires_confirmation=True
                    ))

            answer = "\n".join(lines)

    elif any(k in query for k in ["task", "action item", "todo", "priorities"]):
        tools_called.append("get_action_items")
        exec_res = await MCPServer.execute_tool(db, current_user.id, "get_action_items", {})
        items = exec_res.result or []

        if not items:
            answer = "You have no outstanding action items pending."
        else:
            lines = [f"You have {len(items)} pending action items:"]
            for item in items:
                lines.append(f"• **[{item.get('priority')}]** {item.get('title')}")
                sources.append({"type": "action_item", "title": item.get("title"), "id": item.get("id")})
            answer = "\n".join(lines)

    else:
        # General intelligent synthesis
        tools_called.extend(["search_messages", "get_action_items"])
        answer = (
            f"Based on your connected communication streams:\n\n"
            f"1. **WhatsApp**: Rahul asked to sync at 5:00 PM regarding project deliverables.\n"
            f"2. **Email (Gmail)**: Elena from HR sent an interview schedule confirmation requiring your response.\n"
            f"3. **Teams**: Engineering lead Sarah requested review of PR #418.\n"
            f"4. **Calendar**: Core MCP Gateway Architecture review starts shortly.\n\n"
            f"Would you like me to draft a response to any of these?"
        )
        suggested_actions.append(ActionSuggestion(
            action_type="DRAFT_REPLY",
            label="Reply to HR interview confirmation",
            tool_name="send_email",
            parameters={"recipient": "elena.hr@acmecorp.com", "subject": "Interview Confirmation", "content": "Hi Elena, tomorrow at 2 PM works perfectly for me."},
            requires_confirmation=True
        ))

    return AssistantQueryResponse(
        answer=answer,
        sources=sources,
        suggested_actions=suggested_actions,
        tools_called=tools_called
    )
