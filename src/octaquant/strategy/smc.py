from __future__ import annotations

from .models import Candle


def detect_order_block(candles: list[Candle]) -> tuple[float, float] | None:
    if len(candles) < 4:
        return None
    pivot = candles[-4]
    if candles[-1].close > pivot.high:
        return (pivot.low, pivot.high)
    if candles[-1].close < pivot.low:
        return (pivot.low, pivot.high)
    return None


def detect_value_gap(candles: list[Candle]) -> tuple[float, float] | None:
    if len(candles) < 3:
        return None
    c1, _, c3 = candles[-3], candles[-2], candles[-1]
    if c1.high < c3.low:
        return (c1.high, c3.low)
    if c1.low > c3.high:
        return (c3.high, c1.low)
    return None


def detect_retail_trap(candles: list[Candle], volume_multiplier: float = 1.8) -> bool:
    if len(candles) < 20:
        return False
    recent = candles[-20:]
    avg_volume = sum(c.volume for c in recent[:-1]) / (len(recent) - 1)
    last = recent[-1]
    price_range = max(last.high - last.low, 1e-6)
    body = abs(last.close - last.open)
    low_movement = (body / price_range) < 0.25
    return last.volume > (avg_volume * volume_multiplier) and low_movement
