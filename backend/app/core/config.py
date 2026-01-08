from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "DDX - Sistema Médico con IA"
    DEBUG: bool = True

    # ✅ Async driver por defecto
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ddx"

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # N8N Integration
    N8N_API_URL: str = ""
    N8N_API_KEY: str = ""
    N8N_WEBHOOK_URL: str = ""
    BACKEND_URL: str = "http://localhost:8612"

    SECRET_KEY: str = "cambia-esta-clave-en-.env"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # CSV o "*"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return []
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
