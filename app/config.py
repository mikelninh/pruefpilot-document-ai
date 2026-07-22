from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "demo")
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", str(5 * 1024 * 1024)))
    db_path: str = os.getenv(
        "PRUEFPILOT_DB_PATH",
        "/tmp/pruefpilot.db" if os.getenv("VERCEL") else str(ROOT / "data" / "pruefpilot.db"),
    )
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5")
    mistral_api_key: str | None = os.getenv("MISTRAL_API_KEY")
    mistral_model: str = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
    local_model_url: str | None = os.getenv("LOCAL_MODEL_URL")
    allowed_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "https://mikelninh.github.io,https://pruefpilot-aconium.vercel.app,http://localhost:8000,http://127.0.0.1:8000",
        ).split(",")
        if origin.strip()
    )


settings = Settings()
