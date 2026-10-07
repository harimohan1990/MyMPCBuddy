import re
from typing import Optional


class PromptSanitizer:
    """
    Guards the AI Assistant from prompt injection attacks embedded inside
    untrusted emails, Teams messages, WhatsApp chats, or GitHub comments.
    """

    SUSPICIOUS_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"system\s*prompt\s*override", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+(in\s+)?(developer\s+mode|dan)", re.IGNORECASE),
        re.compile(r"send\s+(all|my)\s+(emails|data|messages|tokens)\s+to", re.IGNORECASE),
        re.compile(r"api[_-]?key\s*[:=]", re.IGNORECASE),
    ]

    @classmethod
    def sanitize_external_text(cls, text: str) -> str:
        if not text:
            return ""
        
        # Remove null bytes or control characters
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text)
        
        # Check and flag potential prompt injection attempts
        for pattern in cls.SUSPICIOUS_PATTERNS:
            if pattern.search(cleaned):
                cleaned = pattern.sub("[REDACTED_POTENTIAL_INJECTION]", cleaned)
        
        return cleaned

    @classmethod
    def wrap_as_untrusted(cls, source_name: str, content: str) -> str:
        """
        Wraps content in unambiguous non-executable system boundaries
        so the LLM treats it strictly as passive data.
        """
        sanitized = cls.sanitize_external_text(content)
        return (
            f"\n<<<UNTRUSTED_EXTERNAL_COMMUNICATION_BEGIN source=\"{source_name}\">>>\n"
            f"{sanitized}\n"
            f"<<<UNTRUSTED_EXTERNAL_COMMUNICATION_END>>>\n"
        )
