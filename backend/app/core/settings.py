from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/app/core/settings.py -> parents[2] = backend/
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    # si ya tienes database_url, déjalo como lo tengas
    database_url: str | None = None

    # ✅ importante: lo hacemos opcional para que la app no reviente
    # y validamos nosotros en el endpoint
    DIPOMEX_APIKEY: str = ""

    DIPOMEX_ENDPOINT: str = "https://api.tau.com.mx/dipomex/v1/codigo_postal"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,  # en Windows da igual, pero ayuda
    )


settings = Settings()
