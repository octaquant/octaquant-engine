from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import random

from octaquant.strategy.models import Candle
from octaquant.strategy.gamma_blast import OptionChainRow


@dataclass(slots=True)
class DhanHQClient:
    api_key: str = "demo"

    async def fetch_candles(self, symbol: str, count: int = 100) -> list[Candle]:
        base = random.uniform(100, 500)
        now = datetime.utcnow()
        candles: list[Candle] = []
        price = base
        for i in range(count):
            ts = now - timedelta(minutes=count - i)
            move = random.uniform(-3, 3)
            open_p = price
            close = max(1.0, open_p + move)
            high = max(open_p, close) + abs(random.uniform(0, 1.5))
            low = min(open_p, close) - abs(random.uniform(0, 1.5))
            volume = random.uniform(1000, 10000)
            candles.append(Candle(ts, open_p, high, low, close, volume))
            price = close
        return candles

    async def fetch_option_chain(self, symbol: str) -> list[OptionChainRow]:
        chain = []
        for strike in range(21000, 21600, 100):
            chain.append(
                OptionChainRow(
                    strike=float(strike),
                    call_oi=random.randint(1000, 20000),
                    put_oi=random.randint(1000, 20000),
                    gamma=random.uniform(-0.8, 0.8),
                )
            )
        return chain


@dataclass(slots=True)
class DeltaExchangeClient:
    api_key: str = "demo"

    async def fetch_candles(self, symbol: str, count: int = 100) -> list[Candle]:
        return await DhanHQClient().fetch_candles(symbol, count)


@dataclass(slots=True)
class ForexClientPlaceholder:
    provider: str = "MT5/OANDA"

    async def fetch_candles(self, symbol: str, count: int = 100) -> list[Candle]:
        return await DhanHQClient().fetch_candles(symbol, count)
