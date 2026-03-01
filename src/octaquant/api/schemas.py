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


class PaperTradeRequest(BaseModel):
    symbol: str
    side: str = "BUY"
    entry: float
    stop_loss: float
    take_profit: float | None = None
    account_size: float


class ProbabilityPoint(BaseModel):
    trade_number: int
    probability_of_profit: float


class ProbabilityCurveResponse(BaseModel):
    points: list[ProbabilityPoint]


class ValidationLockStatus(BaseModel):
    thirty_day_pnl: float
    restricted: bool
