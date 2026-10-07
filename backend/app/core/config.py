from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal MCP Hub"
    API_V1_STR: str = "/api/v1"
    
    # Security & Encryption
    SECRET_KEY: str = "c93b68f9a2f7c00e57209d7b415e612bbd63259a4a75be418d172e2cf648c691"
    # AES-256-GCM requires 32 bytes (base64 encoded here: 44 chars)
    ENCRYPTION_KEY: str = "tQe6z6uJ7f6X4vL8x1b9P3k7W2q8Z4m1Y9r3E6v8N0s="
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    # Database & Redis
    DATABASE_URL: str = "sqlite+aiosqlite:///./mcp_hub.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Google OAuth (Gmail & Google Calendar)
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/oauth/callback/google"

    # Microsoft Graph OAuth
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_REDIRECT_URI: str = "http://localhost:3000/oauth/callback/microsoft"

    # GitHub OAuth
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""
    GITHUB_REDIRECT_URI: str = "http://localhost:3000/oauth/callback/github"

    # AI Configuration
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
