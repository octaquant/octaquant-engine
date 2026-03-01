from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(slots=True)
class MonteCarloResult:
    risk_of_ruin: float
    accepted: bool


def monte_carlo_risk_of_ruin(
    iterations: int,
    initial_capital: float,
    risk_per_trade: float,
    win_rate: float,
    rr: float,
    ruin_threshold: float = 0.5,
    max_allowed_ror: float = 0.20,
) -> MonteCarloResult:
    ruined = 0
    for _ in range(iterations):
        capital = initial_capital
        for _ in range(100):
            stake = capital * risk_per_trade
            if random.random() <= win_rate:
                capital += stake * rr
            else:
                capital -= stake
            if capital <= initial_capital * ruin_threshold:
                ruined += 1
                break
    ror = ruined / iterations
    return MonteCarloResult(risk_of_ruin=ror, accepted=ror <= max_allowed_ror)
