from typing import Dict, Type, Optional
from app.providers.base import CommunicationProvider
from app.providers.gmail.adapter import GmailProvider
from app.providers.whatsapp.adapter import WhatsAppProvider
from app.providers.teams.adapter import TeamsProvider
from app.providers.github.adapter import GitHubProvider
from app.providers.calendar.adapter import CalendarProvider
from app.core.security import decrypt_token


class ProviderRegistry:
    _providers: Dict[str, Type[CommunicationProvider]] = {
        "gmail": GmailProvider,
        "whatsapp": WhatsAppProvider,
        "teams": TeamsProvider,
        "github": GitHubProvider,
        "calendar": CalendarProvider,
    }

    @classmethod
    def register(cls, name: str, provider_cls: Type[CommunicationProvider]):
        cls._providers[name.lower()] = provider_cls

    @classmethod
    def get(
        cls,
        name: str,
        encrypted_access_token: str,
        encrypted_refresh_token: Optional[str] = None,
        account_id: Optional[str] = None
    ) -> Optional[CommunicationProvider]:
        provider_cls = cls._providers.get(name.lower())
        if not provider_cls:
            return None

        access_token = decrypt_token(encrypted_access_token) if encrypted_access_token else ""
        refresh_token = decrypt_token(encrypted_refresh_token) if encrypted_refresh_token else None

        return provider_cls(
            access_token=access_token,
            refresh_token=refresh_token,
            account_id=account_id
        )

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._providers.keys())
