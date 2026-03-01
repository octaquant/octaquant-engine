from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import select, func

from octaquant.core.config import ExecutionMode, settings
from octaquant.db.models import TradeLog
from octaquant.db.session import SessionLocal
from octaquant.strategy.models import TradeSignal
from octaquant.strategy.risk import monte_carlo_risk_of_ruin


@dataclass(slots=True)
class ExecutionDecision:
    approved: bool
    reason: str


class TradeExecutor:
    async def can_switch_live(self) -> bool:
        cutoff = datetime.utcnow() - timedelta(days=settings.validation_days_required)
        async with SessionLocal() as session:
            query = select(func.count()).select_from(TradeLog).where(TradeLog.created_at <= cutoff)
            total = (await session.execute(query)).scalar_one()
            return total > 0

    async def pre_trade_risk_gate(self, rr: float) -> ExecutionDecision:
        if rr < settings.min_rr or rr > settings.max_rr:
            return ExecutionDecision(False, "RR outside allowed range")

        mc = monte_carlo_risk_of_ruin(
            iterations=settings.monte_carlo_iterations,
            initial_capital=100_000,
            risk_per_trade=0.01,
            win_rate=0.45,
            rr=rr,
            max_allowed_ror=settings.max_risk_of_ruin,
        )
        if not mc.accepted:
            return ExecutionDecision(False, f"Risk of ruin too high: {mc.risk_of_ruin:.2%}")
        return ExecutionDecision(True, f"Accepted with ROR {mc.risk_of_ruin:.2%}")

    async def execute(self, signal: TradeSignal) -> ExecutionDecision:
        decision = await self.pre_trade_risk_gate(signal.rr)
        if not decision.approved:
            return decision

        mode = settings.execution_mode
        if mode == ExecutionMode.LIVE_TRADING and not await self.can_switch_live():
            return ExecutionDecision(False, "30-day validation gate not met")

        async with SessionLocal() as session:
            session.add(
                TradeLog(
                    symbol=signal.symbol,
                    side=signal.side.value,
                    entry=signal.entry,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    rr=signal.rr,
                    mode=mode.value,
                )
            )
            await session.commit()
        return ExecutionDecision(True, f"Executed in {mode.value}")
