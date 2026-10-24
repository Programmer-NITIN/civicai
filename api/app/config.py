"""
config.py
---------
Centralized application settings for CivicAI.

All environment variables are read through this module exclusively.
No other module reads from .env directly — this is the single source of truth
for configuration across the entire application.

Security notes:
- In production (DEBUG=false) set ALLOWED_ORIGINS to a comma-separated list of
  trusted frontend domains. Wildcard CORS is only permitted when DEBUG=true.
- Set DOCS_ENABLED=false before going live to hide /docs and /redoc.
- Never commit real API keys to source code or .env.example.
"""

import logging
from typing import Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

# ── Logging Configuration ────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("civicai")


class Settings(BaseSettings):
    """Application-wide configuration backed by environment variables.

    All fields have safe defaults so the app can boot without any .env file.
    Vision AI integration defaults to mock mode — enabling requires a key.
    """

    app_name: str = "AMC CivicAI"
    app_version: str = "1.0.0"
    debug: bool = True

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, v: Any) -> bool:
        """Accept flexible truthy strings for the DEBUG flag."""
        if isinstance(v, str):
            return v.lower() in ("true", "t", "1", "yes", "y", "on")
        return bool(v)

    # ── Security ──────────────────────────────────────────────────────────────
    allowed_origins_raw: str = ""
    docs_enabled: bool = True

    @field_validator("allowed_origins_raw", mode="before")
    @classmethod
    def parse_origins_raw(cls, v: Any) -> str:
        """Accept list or str from env; always normalize to str."""
        if isinstance(v, list):
            return ",".join(v)
        return str(v) if v else ""

    @property
    def allowed_origins(self) -> List[str]:
        """Returns the effective CORS origin list.

        - Debug mode  → ["*"] unless explicitly overridden.
        - Prod  mode  → parsed ALLOWED_ORIGINS; empty list blocks all CORS.
        """
        if self.allowed_origins_raw.strip():
            return [
                o.strip()
                for o in self.allowed_origins_raw.split(",")
                if o.strip()
            ]
        if self.debug:
            return ["*"]
        return []

    # ── Vision AI ─────────────────────────────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_timeout_seconds: int = 8

    # ── Upload limits ─────────────────────────────────────────────────────────
    max_upload_size_mb: int = 10

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Singleton instance — imported by all modules
settings = Settings()
