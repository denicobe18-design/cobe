"""Lokalna L2 knjiga iz Binance diff-depth toka, usklađena sa snapshotom."""

from __future__ import annotations

from typing import Any


class OrderBook:
    def __init__(self, depth: int = 50) -> None:
        self.depth = depth
        self.bids: dict[float, float] = {}
        self.asks: dict[float, float] = {}
        self.last_id: int | None = None
        self.synced = False
        self.dirty = False
        self.buffer: list[dict[str, Any]] = []

    def load_snapshot(self, last_id: int, bids: list, asks: list) -> None:
        self.bids = {float(price): float(qty) for price, qty in bids if float(qty) > 0}
        self.asks = {float(price): float(qty) for price, qty in asks if float(qty) > 0}
        self.last_id = int(last_id)
        self.synced = True
        self.dirty = False
        pending = self.buffer
        self.buffer = []
        for event in pending:
            self.apply(event)

    def apply(self, event: dict[str, Any]) -> None:
        if not self.synced or self.last_id is None:
            self.buffer.append(event)
            if len(self.buffer) > 1000:
                self.buffer = self.buffer[-400:]
            return
        first_id = int(event["U"])
        final_id = int(event["u"])
        if final_id < self.last_id:
            return
        if first_id > self.last_id + 1:
            self.synced = False
            self.dirty = True
            self.buffer = [event]
            return
        self._side(self.bids, event.get("b") or [])
        self._side(self.asks, event.get("a") or [])
        self.last_id = final_id

    @staticmethod
    def _side(book: dict[float, float], updates: list) -> None:
        for price_raw, qty_raw in updates:
            price = float(price_raw)
            qty = float(qty_raw)
            if qty == 0.0:
                book.pop(price, None)
            else:
                book[price] = qty

    def top(self) -> tuple[tuple[tuple[float, float], ...], tuple[tuple[float, float], ...]]:
        bids = tuple(sorted(self.bids.items(), key=lambda row: row[0], reverse=True)[: self.depth])
        asks = tuple(sorted(self.asks.items(), key=lambda row: row[0])[: self.depth])
        return bids, asks
