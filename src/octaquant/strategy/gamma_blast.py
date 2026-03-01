from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class OptionChainRow:
    strike: float
    call_oi: int
    put_oi: int
    gamma: float


@dataclass(slots=True)
class GammaSignal:
    oi_spike: bool
    gamma_shift: bool


def analyze_nse_gamma_blast(option_chain: list[OptionChainRow]) -> GammaSignal:
    if len(option_chain) < 2:
        return GammaSignal(oi_spike=False, gamma_shift=False)

    total_oi = [row.call_oi + row.put_oi for row in option_chain]
    gamma_values = [row.gamma for row in option_chain]
    oi_spike = max(total_oi) > (sum(total_oi) / len(total_oi)) * 1.5

    mid = len(gamma_values) // 2
    left = sum(gamma_values[:mid])
    right = sum(gamma_values[mid:])
    gamma_shift = (left < 0 < right) or (left > 0 > right)

    return GammaSignal(oi_spike=oi_spike, gamma_shift=gamma_shift)
