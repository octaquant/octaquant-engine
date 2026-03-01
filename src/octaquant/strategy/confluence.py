from __future__ import annotations

from octaquant.core.config import settings
from octaquant.strategy.gamma_blast import analyze_nse_gamma_blast
from octaquant.strategy.indicators import ema, fib_retracement
from octaquant.strategy.models import Side, TradeSignal
from octaquant.strategy.smc import detect_order_block, detect_retail_trap, detect_value_gap


class ConfluenceStrategy:
    def generate_signal(self, symbol: str, candles, option_chain=None) -> TradeSignal | None:
        closes = [c.close for c in candles]
        trend_ema = ema(closes, period=26)
        if trend_ema is None:
            return None

        last = candles[-1]
        side = Side.LONG if last.close > trend_ema else Side.SHORT

        order_block = detect_order_block(candles)
        value_gap = detect_value_gap(candles)
        retail_trap = detect_retail_trap(candles)

        swing_low = min(c.low for c in candles[-20:])
        swing_high = max(c.high for c in candles[-20:])
        fib_618 = fib_retracement(swing_low, swing_high, 0.618)
        fib_786 = fib_retracement(swing_low, swing_high, 0.786)

        in_fib_zone = min(fib_618, fib_786) <= last.close <= max(fib_618, fib_786)
        if not (order_block and value_gap and retail_trap and in_fib_zone):
            return None

        gamma_ok = True
        if option_chain is not None:
            gamma = analyze_nse_gamma_blast(option_chain)
            gamma_ok = gamma.oi_spike and gamma.gamma_shift
        if not gamma_ok:
            return None

        if side == Side.LONG:
            stop = min(order_block[0], value_gap[0])
            target = last.close + (last.close - stop) * settings.min_rr
        else:
            stop = max(order_block[1], value_gap[1])
            target = last.close - (stop - last.close) * settings.min_rr

        rr = abs((target - last.close) / (last.close - stop))

        return TradeSignal(
            symbol=symbol,
            side=side,
            entry=last.close,
            stop_loss=stop,
            take_profit=target,
            rr=rr,
            confluences=["26EMA", "OrderBlock", "ValueGap", "RetailTrap", "Fib618/786", "GammaBlast"],
        )
