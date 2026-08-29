"""Application configuration.

Typed settings via pydantic-settings. Every value has a safe default so the demo
runs with no `.env` at all. See `.env.example`.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_", extra="ignore")

    app_name: str = "Product Data Automation API"
    document_extractor: str = "mock"    # only "mock" ships in this repo
    llm_provider: str = "mock"
    image_provider: str = "mock"

    # generic pricing knobs (illustrative — see app/domain/pricing.py)
    landed_cost_factor: float = 1.15
    retail_multiplier: float = 2.5

    storage_dir: Path = Field(default=_REPO_ROOT / "demo_data" / "_storage_out")
    cors_origins: list[str] = ["http://localhost:5173"]

    demo_data_dir: Path = _REPO_ROOT / "demo_data"


settings = Settings()
