from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Side(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(slots=True)
class Candle:
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(slots=True)
class TradeSignal:
    symbol: str
    side: Side
    entry: float
    stop_loss: float
    take_profit: float
    rr: float
    confluences: list[str] = field(default_factory=list)
