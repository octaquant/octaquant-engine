from __future__ import annotations

import asyncio

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from octaquant.core.config import ExecutionMode

from octaquant.api.schemas import (
    EngineStatus,
    PaperTradeRequest,
    ProbabilityCurveResponse,
    SignalRequest,
    ValidationLockStatus,
)
from octaquant.core.config import settings
from octaquant.db.models import Base
from octaquant.db.session import engine
from octaquant.execution.service import TradeExecutor
from octaquant.integrations.markets import DhanHQClient, DeltaExchangeClient, ForexClientPlaceholder
from octaquant.streaming.market_hub import MarketHub
from octaquant.strategy.confluence import ConfluenceStrategy
from octaquant.strategy.models import SignalSide, TradeSignal

app = FastAPI(title="OctaQuant")
hub = MarketHub()
strategy = ConfluenceStrategy()
executor = TradeExecutor()
app.mount("/static", StaticFiles(directory="static"), name="static")

SCAN_TARGETS = [
    ("india", "NIFTY", DhanHQClient),
    ("india", "BANKNIFTY", DhanHQClient),
    ("crypto", "BTCUSD", DeltaExchangeClient),
    ("forex", "EURUSD", ForexClientPlaceholder),
]


async def run_startup_scans() -> None:
    settings.execution_mode = ExecutionMode.PAPER_TRADING
    while True:
        for market, symbol, client_cls in SCAN_TARGETS:
            client = client_cls()
            option_chain = await client.fetch_option_chain(symbol) if market == "india" else None
            candles = await client.fetch_candles(symbol)
            signal = strategy.generate_signal(symbol, candles, option_chain)
            if signal is not None:
                await executor.execute(signal)
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    asyncio.create_task(hub.heartbeat_loop())
    asyncio.create_task(run_startup_scans())


@app.get("/status", response_model=EngineStatus)
async def status() -> EngineStatus:
    return EngineStatus(
        name=settings.app_name,
        mode=settings.execution_mode.value,
        validation_days_required=settings.validation_days_required,
        monte_carlo_iterations=settings.monte_carlo_iterations,
    )


@app.get("/")
async def dashboard() -> RedirectResponse:
    return RedirectResponse(url="/static/index.html")


@app.post("/scan-and-trade")
async def scan_and_trade(req: SignalRequest) -> dict:
    market = req.market.lower()
    if market == "india":
        client = DhanHQClient()
        option_chain = await client.fetch_option_chain(req.symbol)
    elif market == "crypto":
        client = DeltaExchangeClient()
        option_chain = None
    elif market == "forex":
        client = ForexClientPlaceholder()
        option_chain = None
    else:
        raise HTTPException(status_code=400, detail="market must be one of: india, crypto, forex")

    candles = await client.fetch_candles(req.symbol)
    signal = strategy.generate_signal(req.symbol, candles, option_chain)
    if signal is None:
        return {"executed": False, "reason": "No confluence signal"}

    decision = await executor.execute(signal)
    return {
        "executed": decision.approved,
        "reason": decision.reason,
        "signal": {
            "symbol": signal.symbol,
            "side": signal.side,
            "entry": signal.entry,
            "sl": signal.stop_loss,
            "tp": signal.take_profit,
            "rr": signal.rr,
            "confluences": signal.confluences,
        },
    }


@app.post("/paper-trade")
async def place_paper_trade(req: PaperTradeRequest) -> dict:
    try:
        quantity, risk_amount = executor.calculate_position_size(req.account_size, req.entry, req.stop_loss)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    side = req.side.upper()
    if side not in {"BUY", "SELL"}:
        raise HTTPException(status_code=422, detail="side must be BUY or SELL")

    take_profit = req.take_profit
    if take_profit is None:
        move = abs(req.entry - req.stop_loss) * 2
        take_profit = req.entry + move if side == "BUY" else req.entry - move

    rr = abs(take_profit - req.entry) / abs(req.entry - req.stop_loss)
    trade_signal = TradeSignal(
        symbol=req.symbol,
        side=SignalSide.BUY if side == "BUY" else SignalSide.SELL,
        entry=req.entry,
        stop_loss=req.stop_loss,
        take_profit=take_profit,
        rr=rr,
        confluences=["paper-trade"],
    )

    decision = await executor.execute(trade_signal)
    return {
        "approved": decision.approved,
        "reason": decision.reason,
        "position_size": quantity,
        "risk_amount": risk_amount,
        "risk_percent": 1.0,
    }


@app.get("/monte-carlo/probability-curve", response_model=ProbabilityCurveResponse)
async def monte_carlo_probability_curve() -> ProbabilityCurveResponse:
    points = executor.probability_curve()
    return ProbabilityCurveResponse(points=points)


@app.get("/validation-lock", response_model=ValidationLockStatus)
async def validation_lock() -> ValidationLockStatus:
    pnl = await executor.thirty_day_pnl()
    return ValidationLockStatus(thirty_day_pnl=pnl, restricted=pnl < 0)


@app.websocket("/ws/market")
async def market_socket(ws: WebSocket) -> None:
    await hub.connect(ws)
    try:
        while True:
            _ = await ws.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(ws)
