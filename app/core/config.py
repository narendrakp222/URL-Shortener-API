import os
import re
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# libpq-only query parameters that the asyncpg driver rejects outright.
_LIBPQ_ONLY_PARAMS = {
    "sslmode",
    "sslrootcert",
    "sslcert",
    "sslkey",
    "channel_binding",
    "gssencmode",
    "application_name",
    "options",
}


class Settings(BaseSettings):
    """
    Application Settings powered by Pydantic BaseSettings.
    Automatically reads environment variables and .env file.
    """
    PROJECT_NAME: str = "Production URL Shortener API"
    API_V1_STR: str = "/api/v1"
    BASE_URL: str = "http://localhost:8000"
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database Settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./url_shortener.db"

    # CORS configuration
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def split_comma_separated(cls, v: object) -> object:
        """
        Accept comma-separated values so list settings can be supplied through
        plain environment variables on PaaS platforms (Vercel, Render).
        """
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                return v
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        """
        Helper to convert postgres:// or postgresql:// to postgresql+asyncpg://
        for Render or Heroku postgres connection strings.
        """
        if isinstance(v, str):
            if v.startswith("postgres://"):
                v = v.replace("postgres://", "postgresql+asyncpg://", 1)
            elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

            # asyncpg rejects libpq-only query parameters (?sslmode=require,
            # ?channel_binding=require) that Neon, Supabase and Heroku append.
            if v.startswith("postgresql+asyncpg://") and "?" in v:
                base, _, query = v.partition("?")
                kept = [
                    pair for pair in query.split("&")
                    if pair and pair.split("=", 1)[0].lower() not in _LIBPQ_ONLY_PARAMS
                ]
                v = f"{base}?{'&'.join(kept)}" if kept else base
        return v


settings = Settings()

# Vercel serves the app from a read-only filesystem, so a file-backed SQLite
# database cannot be used there unless it points at /tmp.
IS_VERCEL: bool = any(os.getenv(name) for name in ("VERCEL", "VERCEL_ENV"))

# A wildcard origin is incompatible with allow_credentials=True (browsers reject
# the response), so it is expressed as an origin regex instead.
CORS_ALLOW_ALL: bool = "*" in settings.BACKEND_CORS_ORIGINS
CORS_ORIGINS: List[str] = [] if CORS_ALLOW_ALL else settings.BACKEND_CORS_ORIGINS
CORS_ORIGIN_REGEX: str | None = r".*" if CORS_ALLOW_ALL else None
CORS_ALLOW_CREDENTIALS: bool = True

# Auto-create tables on startup (fresh local SQLite) unless the platform uses
# ephemeral storage. On Vercel the schema must come from Alembic migrations
# unless SQLite is deliberately pointed at /tmp.
AUTO_CREATE_TABLES: bool = not IS_VERCEL or settings.DATABASE_URL.startswith("sqlite")
