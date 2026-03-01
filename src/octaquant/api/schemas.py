from __future__ import annotations

from pydantic import BaseModel


class SignalRequest(BaseModel):
    market: str
    symbol: str


class EngineStatus(BaseModel):
    name: str
    mode: str
    validation_days_required: int
    monte_carlo_iterations: int
