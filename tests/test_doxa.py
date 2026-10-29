"""Mehanika agenata, knjige, naknade i traila. Bez mreže."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from doxa.agents import assess_btc, evaluate
from doxa.engine import Engine
from doxa.indicators import atr, bullish_engulfing, ema, fractional_kelly, order_book_imbalance, rsi
from doxa.orderbook import OrderBook
from doxa.teacher import Teacher
from doxa.types import BookTop, Candle, Decision, Doctrine, MarketSnapshot, Stats


def _candle(index: int, open_: float, close: float, volume: float = 100.0, width: int = 60_000) -> Candle:
    high = max(open_, close) + 0.05
    low = min(open_, close) - 0.05
    return Candle(index * width, open_, high, low, close, volume)


def _trend(count: int, start: float, step: float, volume: float = 100.0, width: int = 60_000) -> list[Candle]:
    candles = []
    price = start
    for index in range(count):
        nxt = price + step
        candles.append(_candle(index, price, nxt, volume, width))
        price = nxt
    return candles


def _book(bid: float, ask: float, bid_qty: float = 8.0, ask_qty: float = 1.0) -> BookTop:
    bids = tuple((bid - index * 0.01, bid_qty) for index in range(20))
    asks = tuple((ask + index * 0.01, ask_qty) for index in range(20))
    return BookTop(bids, asks, 20, True)


def _snapshot(symbol: str, c15, c1h, c4h, btc, book: BookTop, funding: float = 0.0001) -> MarketSnapshot:
    return MarketSnapshot(
        now_ms=1_800_000_000_000,
        books={symbol: book, "BTCUSDT": _book(60_000, 60_010, 2, 2)},
        candles={
            symbol: {"15m": tuple(c15), "1h": tuple(c1h), "4h": tuple(c4h)},
            "BTCUSDT": {"1m": tuple(btc), "15m": tuple(btc[:40])},
        },
        forming={},
        live={symbol: book.bid or 0.0},
        funding={symbol: funding},
        hub_status="TEST",
        hub_error="",
        ready=True,
    )


def _pullback_1h() -> list[Candle]:
    candles = _trend(48, 100, 0.45, width=3_600_000)
    price = candles[-1].close
    start = candles[-1].open_time
    for step in range(1, 14):
        nxt = price - 0.7
        candles.append(Candle(start + step * 3_600_000, price, price, nxt, nxt, 90))
        price = nxt
        values = [candle.close for candle in candles]
        now = rsi(values, 14)
        prev = rsi(values[:-1], 14)
        if now and prev and 40 <= now <= 55 and now < prev:
            return candles
    return candles


def _fifteen() -> list[Candle]:
    candles = _trend(40, 80, 0.25, volume=120, width=900_000)
    prev = candles[-2]
    red_open = prev.close + 0.3
    red_close = prev.close - 0.25
    red = Candle(prev.open_time, red_open, red_open + 0.05, red_close - 0.05, red_close, 80)
    green_close = red_open + 1.2
    green = Candle(
        candles[-1].open_time,
        red_close - 0.05,
        green_close + 0.1,
        red_close - 0.1,
        green_close,
        500,
    )
    candles[-2] = red
    candles[-1] = green
    return candles


def _flat_btc() -> list[Candle]:
    candles = []
    price = 60_000.0
    for index in range(40):
        candles.append(Candle(index * 60_000, price, price + 8, price - 8, price + 1, 10))
        price += 1
    return candles


class IndicatorTests(unittest.TestCase):
    def test_rsi_extremes_and_ema_flat(self) -> None:
        rising = [float(index) for index in range(1, 30)]
        self.assertEqual(rsi(rising, 14), 100.0)
        flat = [5.0] * 30
        self.assertAlmostEqual(ema(flat, 9) or 0, 5.0, places=6)
        self.assertAlmostEqual(rsi(flat, 14) or 0, 50.0, places=6)

    def test_atr_and_engulfing(self) -> None:
        candles = [_candle(index, 10, 10) for index in range(20)]
        self.assertAlmostEqual(atr(candles, 14) or 0, 0.1, places=6)
        pair = [
            Candle(0, 10, 10.2, 8, 8.5, 10),
            Candle(1, 8.4, 11, 8.2, 10.5, 20),
        ]
        self.assertTrue(bullish_engulfing(pair))

    def test_imbalance_and_kelly(self) -> None:
        self.assertAlmostEqual(order_book_imbalance([(10, 3)], [(10, 1)]) or 0, 0.75, places=6)
        sized = fractional_kelly(0.52, 1.4, 0.5, 0.30)
        self.assertAlmostEqual(sized, 0.088571, places=4)
        self.assertEqual(fractional_kelly(0.2, 1.0, 0.5, 0.3), 0.0)


class BookTests(unittest.TestCase):
    def test_snapshot_apply_and_gap(self) -> None:
        book = OrderBook(depth=10)
        book.apply({"U": 101, "u": 102, "b": [["10", "2"]], "a": [["11", "1"]]})
        self.assertFalse(book.synced)
        book.load_snapshot(100, [["10", "1"], ["9", "1"]], [["11", "1"]])
        self.assertTrue(book.synced)
        self.assertGreater(book.bids[10.0], 0)
        book.apply({"U": 103, "u": 104, "b": [["10", "0"]], "a": []})
        self.assertNotIn(10.0, book.bids)
        book.apply({"U": 120, "u": 121, "b": [], "a": []})
        self.assertTrue(book.dirty)
        self.assertFalse(book.synced)


class AgentTests(unittest.TestCase):
    def _market(self, funding: float = 0.0001, breakout_volume: float = 500):
        c15 = _fifteen()
        if breakout_volume != 500:
            last = c15[-1]
            c15[-1] = Candle(last.open_time, last.open, last.high, last.low, last.close, breakout_volume)
        c4 = _trend(80, 50, 0.4, width=14_400_000)
        c1 = _pullback_1h()
        last = c15[-1].close
        book = _book(last, last * 1.0002, bid_qty=9, ask_qty=0.6)
        return _snapshot("SOLUSDT", c15, c1, c4, _flat_btc(), book, funding)

    def test_entry_when_stack_agrees(self) -> None:
        decision = evaluate(self._market(), "SOLUSDT", Doctrine(), Stats())
        self.assertTrue(decision.allow, decision.reason + " | " + " ; ".join(view.detail for view in decision.views))
        self.assertGreater(decision.stake_fraction, 0)

    def test_skeptic_veto(self) -> None:
        decision = evaluate(self._market(funding=0.001, breakout_volume=10), "SOLUSDT", Doctrine(), Stats())
        self.assertFalse(decision.allow)
        self.assertIn("Skeptik", decision.reason)

    def test_btc_guard_triggers(self) -> None:
        candles = _flat_btc()
        start = candles[-1].close
        for index, price in enumerate((start * 0.996, start * 0.992, start * 0.990)):
            candles.append(Candle((40 + index) * 60_000, start, start, price, price, 800))
            start = price
        snap = self._market()
        snap = MarketSnapshot(
            now_ms=snap.now_ms,
            books=snap.books,
            candles={**snap.candles, "BTCUSDT": {"1m": tuple(candles), "15m": snap.candles["BTCUSDT"]["15m"]}},
            forming={},
            live=snap.live,
            funding=snap.funding,
            hub_status="TEST",
            hub_error="",
            ready=True,
        )
        triggered, delta, ratio, _detail = assess_btc(snap, Doctrine())
        self.assertTrue(triggered, msg=f"delta={delta} ratio={ratio}")
        decision = evaluate(snap, "SOLUSDT", Doctrine(), Stats())
        self.assertFalse(decision.allow)
        self.assertEqual(decision.views[1].state, "freeze")


class EngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        os.environ["DOXA_WALLET"] = str(Path(self._tmp.name) / "wallet.json")
        self.engine = Engine()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _decision(self) -> Decision:
        return Decision(
            symbol="SOLUSDT",
            allow=True,
            reason="test",
            stake_fraction=0.10,
            score=1,
            setup=True,
            views=(),
            metrics={
                "imbalance": 0.82,
                "veto_flags": [],
                "sentiment": "NEUTRAL",
                "atr": 8.0,
                "rsi4h": 50,
                "funding": 0.0001,
            },
        )

    def _priced(self, bid: float, ask: float) -> MarketSnapshot:
        book = BookTop(((bid, 5.0),), ((ask, 5.0),), 1, True)
        return MarketSnapshot(
            now_ms=1_800_000_000_000,
            books={"SOLUSDT": book},
            candles={"SOLUSDT": {"15m": ()}},
            forming={},
            live={"SOLUSDT": bid},
            funding={},
            hub_status="TEST",
            hub_error="",
            ready=True,
        )

    def test_open_charges_fee_and_trail_locks_profit(self) -> None:
        snap = self._priced(99.98, 100.0)
        self.engine._open(self._decision(), snap, 1_800_000_000)
        self.assertEqual(len(self.engine.wallet.positions), 1)
        position = self.engine.wallet.positions[0]
        self.assertLess(self.engine.wallet.cash, 185)
        self.assertGreater(position.fees, 0)
        entry = position.entry
        up_be = self._priced(entry * 1.04, entry * 1.0402)
        self.assertTrue(self.engine._manage(position, up_be, False))
        self.assertAlmostEqual(position.sl, entry, places=4)
        self.assertFalse(position.partial_done)
        position.context["atr"] = 0.4
        up_partial = self._priced(entry * 1.06, entry * 1.0602)
        self.assertTrue(self.engine._manage(position, up_partial, False))
        self.assertTrue(position.partial_done)
        self.assertLess(position.qty, position.initial_qty * 0.6)
        self.assertGreater(position.sl, entry)
        trail_hit = self._priced(position.sl - 0.2, position.sl)
        self.assertFalse(self.engine._manage(position, trail_hit, False))
        self.assertEqual(len(self.engine.wallet.closed), 1)
        self.assertEqual(self.engine.wallet.closed[0]["reason"], "TRAIL")
        self.assertGreater(self.engine.wallet.closed[0]["fees"], 0)

    def test_freeze_flattens_between_stop_and_entry(self) -> None:
        snap = self._priced(99.98, 100.0)
        self.engine._open(self._decision(), snap, 1_800_000_000)
        position = self.engine.wallet.positions[0]
        mid = self._priced(position.entry * 0.995, position.entry * 0.996)
        self.assertGreater(mid.books["SOLUSDT"].bid or 0, position.sl)
        self.assertTrue(self.engine._manage(position, mid, False))
        self.assertFalse(self.engine._manage(position, mid, True))
        self.assertEqual(self.engine.wallet.closed[-1]["reason"], "BTC_FREEZE")

    def test_teacher_tightens_fake_wall(self) -> None:
        doctrine = Doctrine()
        before = doctrine.whale_min
        lessons = Teacher().review_close(
            doctrine,
            pnl=-4,
            mfe=0.01,
            pnl_pct=-0.02,
            context={"imbalance": 0.8, "veto_flags": []},
            stats_n=3,
            win_rate=0.4,
            payoff=1.0,
        )
        self.assertGreater(doctrine.whale_min, before)
        self.assertTrue(lessons)


if __name__ == "__main__":
    unittest.main()
