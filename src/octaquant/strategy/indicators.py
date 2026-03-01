from __future__ import annotations

from typing import Iterable


def ema(values: Iterable[float], period: int = 26) -> float | None:
    series = list(values)
    if len(series) < period:
        return None
    alpha = 2 / (period + 1)
    ema_value = sum(series[:period]) / period
    for price in series[period:]:
        ema_value = (price - ema_value) * alpha + ema_value
    return ema_value


def fib_retracement(swing_low: float, swing_high: float, level: float) -> float:
    distance = swing_high - swing_low
    return swing_high - (distance * level)
