from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class ExecutionMode(str, Enum):
    PAPER_TRADING = "PAPER_TRADING"
    LIVE_TRADING = "LIVE_TRADING"


class Settings(BaseModel):
    app_name: str = "OctaQuant"
    execution_mode: ExecutionMode = ExecutionMode.PAPER_TRADING
    monte_carlo_iterations: int = 10_000
    min_rr: float = 2.0
    max_rr: float = 10.0
    max_risk_of_ruin: float = 0.20
    validation_days_required: int = 30
    websocket_push_seconds: float = 1.0
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/octaquant"
    )


settings = Settings()
