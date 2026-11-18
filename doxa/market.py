"""Javni Binance tok: REST povijest, diff-depth knjiga i kline preko WebSocketa."""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from doxa.config import (
    ALL_SYMBOLS,
    BINANCE_REST,
    BINANCE_WS,
    FUNDING_URL,
    BOOK_LEVELS,
    INTERVAL_MS,
    INTERVALS,
    KLINE_LIMIT,
    MIN_BARS,
)
from doxa.orderbook import OrderBook
from doxa.types import BookTop, Candle, MarketSnapshot

_HEADERS = {"User-Agent": "doxa-quant-core/1.0"}


def _get_json(url: str, params: dict | None = None):
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers=_HEADERS)
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.loads(response.read().decode())


def _candle_from_rest(row: list) -> Candle:
    return Candle(
        open_time=int(row[0]),
        open=float(row[1]),
        high=float(row[2]),
        low=float(row[3]),
        close=float(row[4]),
        volume=float(row[5]),
    )


def _candle_from_kline(payload: dict) -> Candle:
    return Candle(
        open_time=int(payload["t"]),
        open=float(payload["o"]),
        high=float(payload["h"]),
        low=float(payload["l"]),
        close=float(payload["c"]),
        volume=float(payload["v"]),
    )


class MarketHub:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.books = {symbol: OrderBook(BOOK_LEVELS) for symbol in ALL_SYMBOLS}
        self.candles: dict[str, dict[str, list[Candle]]] = {
            symbol: {interval: [] for interval in INTERVALS[symbol]} for symbol in ALL_SYMBOLS
        }
        self.forming: dict[str, dict[str, Candle]] = {}
        self.live: dict[str, float] = {}
        self.funding: dict[str, float] = {}
        self.status = "BOOT"
        self.error = ""
        self.ready = False
        self._last_msg = 0.0
        self._ws = None
        self._stop = False

    def run(self) -> None:
        threading.Thread(target=self._funding_loop, name="doxa-funding", daemon=True).start()
        threading.Thread(target=self._ws_loop, name="doxa-ws", daemon=True).start()
        while not self._stop:
            try:
                if not self.ready:
                    self._bootstrap()
                self._resync_dirty()
                self._watchdog()
                self._set_ready()
            except Exception as exc:
                with self._lock:
                    self.status = "DEGRADED"
                    self.error = str(exc)[:180]
            time.sleep(3)

    def snapshot(self) -> MarketSnapshot:
        with self._lock:
            books = {}
            for symbol, book in self.books.items():
                bids, asks = book.top()
                books[symbol] = BookTop(bids=bids, asks=asks, levels=len(bids), synced=book.synced)
            candles = {
                symbol: {interval: tuple(series) for interval, series in intervals.items()}
                for symbol, intervals in self.candles.items()
            }
            forming = {symbol: dict(intervals) for symbol, intervals in self.forming.items()}
            return MarketSnapshot(
                now_ms=int(time.time() * 1000),
                books=books,
                candles=candles,
                forming=forming,
                live=dict(self.live),
                funding=dict(self.funding),
                hub_status=self.status,
                hub_error=self.error,
                ready=self.ready,
            )

    def _bootstrap(self) -> None:
        for symbol, intervals in INTERVALS.items():
            for interval in intervals:
                with self._lock:
                    have = len(self.candles[symbol][interval])
                if have >= MIN_BARS[interval]:
                    continue
                rows = _get_json(
                    BINANCE_REST + "/api/v3/klines",
                    {"symbol": symbol, "interval": interval, "limit": KLINE_LIMIT},
                )
                now_ms = int(time.time() * 1000)
                closed: list[Candle] = []
                forming = None
                width = INTERVAL_MS[interval]
                for row in rows:
                    candle = _candle_from_rest(row)
                    if candle.open_time + width <= now_ms:
                        closed.append(candle)
                    else:
                        forming = candle
                with self._lock:
                    self.candles[symbol][interval] = closed
                    if forming is not None:
                        self.forming.setdefault(symbol, {})[interval] = forming
                        self.live[symbol] = forming.close
                time.sleep(0.12)
            self._fetch_depth(symbol)
            time.sleep(0.12)

    def _fetch_depth(self, symbol: str) -> None:
        data = _get_json(
            BINANCE_REST + "/api/v3/depth",
            {"symbol": symbol, "limit": 100},
        )
        with self._lock:
            self.books[symbol].load_snapshot(int(data["lastUpdateId"]), data["bids"], data["asks"])
            bids, asks = self.books[symbol].top()
            if bids and asks:
                self.live[symbol] = (bids[0][0] + asks[0][0]) / 2.0

    def _resync_dirty(self) -> None:
        with self._lock:
            dirty = [symbol for symbol, book in self.books.items() if book.dirty or not book.synced]
        for symbol in dirty:
            try:
                self._fetch_depth(symbol)
            except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
                with self._lock:
                    self.error = f"knjiga {symbol}: {exc}"[:180]
            time.sleep(0.15)

    def _set_ready(self) -> None:
        with self._lock:
            bars_ok = True
            for symbol, intervals in INTERVALS.items():
                for interval in intervals:
                    if len(self.candles[symbol][interval]) < MIN_BARS[interval]:
                        bars_ok = False
            books_ok = sum(1 for symbol in ALL_SYMBOLS if self.books[symbol].synced and self.books[symbol].bids)
            self.ready = bars_ok and books_ok >= 5
            if self.ready:
                self.status = "LIVE"
                self.error = ""
            elif self.status != "DEGRADED":
                self.status = "BOOT"

    def _watchdog(self) -> None:
        if self._last_msg and time.time() - self._last_msg > 25 and self._ws is not None:
            try:
                self._ws.close()
            except Exception:
                return

    def _streams(self) -> list[str]:
        names: list[str] = []
        for symbol, intervals in INTERVALS.items():
            lower = symbol.lower()
            names.append(f"{lower}@depth@100ms")
            for interval in intervals:
                names.append(f"{lower}@kline_{interval}")
        return names

    def _ws_loop(self) -> None:
        import websocket

        while not self._stop:
            url = BINANCE_WS + "?streams=" + "/".join(self._streams())
            socket = websocket.WebSocketApp(
                url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
            )
            self._ws = socket
            try:
                socket.run_forever(ping_interval=20, ping_timeout=10)
            except Exception as exc:
                with self._lock:
                    self.status = "DEGRADED"
                    self.error = str(exc)[:180]
            time.sleep(2)

    def _on_message(self, _socket, message: str) -> None:
        self._last_msg = time.time()
        try:
            payload = json.loads(message)
        except json.JSONDecodeError:
            return
        data = payload.get("data", payload)
        if not isinstance(data, dict):
            return
        event = data.get("e")
        if event == "depthUpdate":
            symbol = data.get("s")
            if symbol not in self.books:
                return
            with self._lock:
                self.books[symbol].apply(data)
                if self.books[symbol].synced:
                    bids, asks = self.books[symbol].top()
                    if bids and asks:
                        self.live[symbol] = (bids[0][0] + asks[0][0]) / 2.0
        elif event == "kline":
            self._on_kline(data)

    def _on_kline(self, data: dict) -> None:
        symbol = data.get("s")
        kline = data.get("k") or {}
        interval = kline.get("i")
        if symbol not in self.candles or interval not in self.candles[symbol]:
            return
        candle = _candle_from_kline(kline)
        closed = bool(kline.get("x"))
        with self._lock:
            self.live[symbol] = candle.close
            series = self.candles[symbol][interval]
            if closed:
                if series and series[-1].open_time == candle.open_time:
                    series[-1] = candle
                else:
                    series.append(candle)
                    if len(series) > 500:
                        del series[:-400]
                self.forming.get(symbol, {}).pop(interval, None)
            else:
                self.forming.setdefault(symbol, {})[interval] = candle

    def _on_error(self, _socket, error) -> None:
        with self._lock:
            self.error = str(error)[:180]

    def _on_close(self, _socket, _code, _reason) -> None:
        with self._lock:
            if self.status == "LIVE":
                self.status = "RECONNECT"

    def _funding_loop(self) -> None:
        while not self._stop:
            found: dict[str, float] = {}
            for symbol in ALL_SYMBOLS:
                if not symbol.endswith("USDT"):
                    continue
                inst = symbol[:-4] + "-USDT-SWAP"
                try:
                    payload = _get_json(FUNDING_URL, {"instId": inst})
                    rows = payload.get("data") if isinstance(payload, dict) else None
                    if rows:
                        found[symbol] = float(rows[0]["fundingRate"])
                except (urllib.error.URLError, TimeoutError, KeyError, TypeError, ValueError):
                    continue
                time.sleep(0.15)
            if found:
                with self._lock:
                    self.funding.update(found)
            time.sleep(45)
