from __future__ import annotations

import asyncio
from datetime import datetime

from fastapi import WebSocket


class MarketHub:
    def __init__(self) -> None:
        self.clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self.clients.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self.clients.discard(ws)

    async def broadcast(self, payload: dict) -> None:
        dead = []
        for ws in self.clients:
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    async def heartbeat_loop(self) -> None:
        while True:
            await self.broadcast({"event": "heartbeat", "ts": datetime.utcnow().isoformat()})
            await asyncio.sleep(1.0)
