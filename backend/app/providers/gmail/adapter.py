import base64
import email
from email.mime.text import MIMEText
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import httpx

from app.providers.base import CommunicationProvider, NormalizedEvent, ProviderSender
from app.core.config import settings
from app.core.logging import logger


class GmailProvider(CommunicationProvider):
    """
    Production-grade Gmail Provider Adapter using official Google REST APIs.
    Supports token refresh, message sync, search, reading threads, and sending replies.
    """

    BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"

    @property
    def provider_name(self) -> str:
        return "gmail"

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def refresh_access_token(self) -> Optional[str]:
        if not self.refresh_token:
            return None
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "refresh_token": self.refresh_token,
                        "grant_type": "refresh_token",
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    new_token = data.get("access_token")
                    self.access_token = new_token
                    return new_token
                else:
                    logger.error(f"Gmail token refresh failed: {response.text}")
                    return None
            except Exception as e:
                logger.error(f"Exception during Gmail token refresh: {str(e)}")
                return None

    def _parse_message_payload(self, msg_data: Dict[str, Any]) -> NormalizedEvent:
        msg_id = msg_data.get("id", "")
        thread_id = msg_data.get("threadId", "")
        payload = msg_data.get("payload", {})
        headers = {h.get("name", "").lower(): h.get("value", "") for h in payload.get("headers", [])}
        
        subject = headers.get("subject", "(No Subject)")
        from_header = headers.get("from", "Unknown")
        to_header = headers.get("to", "")
        
        # Parse sender name and email
        sender_name = from_header
        sender_email = from_header
        if "<" in from_header and ">" in from_header:
            parts = from_header.split("<")
            sender_name = parts[0].strip(' "')
            sender_email = parts[1].replace(">", "").strip()

        # Extract body text
        body_text = ""
        if "parts" in payload:
            for part in payload["parts"]:
                mime_type = part.get("mimeType", "")
                if mime_type == "text/plain":
                    data = part.get("body", {}).get("data", "")
                    if data:
                        body_text = base64.urlsafe_b64decode(data.encode('ASCII') + b"==").decode('utf-8', errors='replace')
                        break
        elif "body" in payload and payload["body"].get("data"):
            data = payload["body"]["data"]
            body_text = base64.urlsafe_b64decode(data.encode('ASCII') + b"==").decode('utf-8', errors='replace')

        if not body_text:
            body_text = msg_data.get("snippet", "")

        # Parse date
        internal_date_ms = int(msg_data.get("internalDate", "0"))
        if internal_date_ms > 0:
            msg_time = datetime.fromtimestamp(internal_date_ms / 1000.0, tz=timezone.utc)
        else:
            msg_time = datetime.now(timezone.utc)

        # Basic priority heuristics
        label_ids = msg_data.get("labelIds", [])
        is_important = "IMPORTANT" in label_ids or "STARRED" in label_ids
        priority = "HIGH" if is_important else "MEDIUM"

        return NormalizedEvent(
            provider="gmail",
            provider_event_id=msg_id,
            type="email",
            sender=ProviderSender(name=sender_name, address=sender_email),
            recipient=to_header,
            title=subject,
            content=body_text[:2000],  # sanitized preview length
            timestamp=msg_time,
            priority=priority,
            category="WORK" if any(k in subject.lower() for k in ["interview", "pr", "project", "review", "contract"]) else "PERSONAL",
            action_required=any(term in (subject + " " + body_text).lower() for term in ["please review", "respond", "confirm", "action required", "deadline"]),
            thread_id=thread_id,
            source_url=f"https://mail.google.com/mail/u/0/#inbox/{msg_id}",
            metadata={"labelIds": label_ids, "snippet": msg_data.get("snippet", "")}
        )

    async def fetch_notifications(self, since: Optional[datetime] = None, limit: int = 50) -> List[NormalizedEvent]:
        events: List[NormalizedEvent] = []
        if not self.access_token:
            return events

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                # Query recent unread or inbox messages
                params = {"maxResults": min(limit, 50), "q": "in:inbox"}
                res = await client.get(f"{self.BASE_URL}/messages", headers=self._get_headers(), params=params)
                
                if res.status_code == 401:
                    new_token = await self.refresh_access_token()
                    if new_token:
                        res = await client.get(f"{self.BASE_URL}/messages", headers=self._get_headers(), params=params)

                if res.status_code != 200:
                    logger.error(f"Gmail list messages failed: {res.status_code} {res.text}")
                    return events

                data = res.json()
                message_stubs = data.get("messages", [])
                
                for stub in message_stubs[:limit]:
                    msg_id = stub.get("id")
                    detail_res = await client.get(f"{self.BASE_URL}/messages/{msg_id}?format=full", headers=self._get_headers())
                    if detail_res.status_code == 200:
                        parsed = self._parse_message_payload(detail_res.json())
                        events.append(parsed)

            except Exception as e:
                logger.error(f"Error fetching Gmail notifications: {str(e)}")

        return events

    async def search_messages(self, query: str, limit: int = 20) -> List[NormalizedEvent]:
        events: List[NormalizedEvent] = []
        if not self.access_token:
            return events

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                params = {"maxResults": limit, "q": query}
                res = await client.get(f"{self.BASE_URL}/messages", headers=self._get_headers(), params=params)
                if res.status_code == 200:
                    for stub in res.json().get("messages", []):
                        detail_res = await client.get(f"{self.BASE_URL}/messages/{stub['id']}?format=full", headers=self._get_headers())
                        if detail_res.status_code == 200:
                            events.append(self._parse_message_payload(detail_res.json()))
            except Exception as e:
                logger.error(f"Error searching Gmail: {str(e)}")
        return events

    async def get_message(self, message_id: str) -> Optional[NormalizedEvent]:
        if not self.access_token:
            return None
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                res = await client.get(f"{self.BASE_URL}/messages/{message_id}?format=full", headers=self._get_headers())
                if res.status_code == 200:
                    return self._parse_message_payload(res.json())
            except Exception as e:
                logger.error(f"Error getting Gmail message {message_id}: {str(e)}")
        return None

    async def send_message(self, recipient: str, content: str, subject: Optional[str] = None) -> Dict[str, Any]:
        """Sends an email message via Gmail API."""
        if not self.access_token:
            raise ValueError("Gmail account not authenticated")

        mime_msg = MIMEText(content)
        mime_msg["to"] = recipient
        mime_msg["subject"] = subject or "Re: Update"
        raw_b64 = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode()

        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(
                f"{self.BASE_URL}/messages/send",
                headers=self._get_headers(),
                json={"raw": raw_b64}
            )
            if res.status_code in (200, 201):
                return res.json()
            else:
                raise RuntimeError(f"Gmail send failed ({res.status_code}): {res.text}")
