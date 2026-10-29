"""Tier 1: papirnati broker. Naknada, klizanje, trailing i jedan ulaz po signalu."""

from __future__ import annotations

import threading
import time
from typing import Any

from doxa.agents import assess_btc, evaluate
from doxa.config import GLOBAL_ENTRY_GAP_S, MIN_STAKE_EUR, START_CASH, TRADABLE
from doxa.indicators import atr as atr_indicator
from doxa.notify import notify
from doxa.store import Position, Wallet, fresh_wallet, load_wallet, save_wallet
from doxa.teacher import Teacher
from doxa.types import BookTop, Doctrine, MarketSnapshot, Stats


def slippage(book: BookTop | None, doctrine: Doctrine) -> float:
    half_spread = 0.0001
    if book and book.spread is not None and book.spread > 0:
        half_spread = book.spread / 2.0
    return half_spread + doctrine.impact_bps


def _mark_bid(snapshot: MarketSnapshot, symbol: str) -> float | None:
    book = snapshot.books.get(symbol)
    if book and book.bid:
        return book.bid
    price = snapshot.live.get(symbol)
    return price if price and price > 0 else None


def _mark_ask(snapshot: MarketSnapshot, symbol: str) -> float | None:
    book = snapshot.books.get(symbol)
    if book and book.ask:
        return book.ask
    price = snapshot.live.get(symbol)
    return price if price and price > 0 else None


class Engine:
    def __init__(self, wallet: Wallet | None = None) -> None:
        self.wallet = wallet if wallet is not None else fresh_wallet()
        self.teacher = Teacher()
        self._lock = threading.RLock()
        self.last_snap: MarketSnapshot | None = None
        self._symbol_cooldown: dict[str, float] = {}
        self._last_global_entry = 0.0
        self._last_equity_mark = 0.0
        self.pending_notes: list[str] = []

    @classmethod
    def load(cls) -> Engine:
        return cls(load_wallet())

    def tick(self, snapshot: MarketSnapshot) -> list[str]:
        notes: list[str] = []
        with self._lock:
            self.last_snap = snapshot
            self.pending_notes = []
            now = snapshot.now_ms / 1000.0 if snapshot.now_ms else time.time()
            wallet = self.wallet
            doctrine = wallet.doctrine
            self._expire(now)
            triggered, _delta, _ratio, guard_detail = assess_btc(snapshot, doctrine)
            was_frozen = now < wallet.frozen_until
            if triggered:
                wallet.frozen_until = max(wallet.frozen_until, now + 180.0)
                wallet.freeze_detail = guard_detail
                if not was_frozen:
                    self._note("⚠️ BTC Macro Guard: " + guard_detail, telegram=True)
            frozen = now < wallet.frozen_until
            self._manage_all(snapshot, frozen)
            if wallet.halted:
                self._mark_equity(snapshot, now)
                self._apply_remote()
                save_wallet(wallet)
                notes = list(self.pending_notes)
            else:
                self._maybe_enter(snapshot, now, frozen)
                lessons, wallet.last_relax_at = self.teacher.heartbeat(
                    doctrine,
                    now_s=now,
                    last_entry_at=wallet.last_entry_at,
                    last_relax_at=wallet.last_relax_at,
                    sample_n=self.stats().n,
                )
                for lesson in lessons:
                    self._lesson(lesson)
                self._apply_remote()
                self._mark_equity(snapshot, now)
                save_wallet(wallet)
                notes = list(self.pending_notes)
        for text in notes:
            notify(text)
        return notes

    def stats(self) -> Stats:
        sample = self.wallet.closed[self.wallet.sample_from :]
        wins = [float(item["pnl"]) for item in sample if float(item.get("pnl", 0)) > 0]
        losses = [abs(float(item["pnl"])) for item in sample if float(item.get("pnl", 0)) < 0]
        return Stats(
            n=len(sample),
            wins=len(wins),
            losses=len(losses),
            avg_win=(sum(wins) / len(wins)) if wins else 0.0,
            avg_loss=(sum(losses) / len(losses)) if losses else 0.0,
        )

    def equity(self, snapshot: MarketSnapshot | None = None) -> float:
        snap = snapshot or self.last_snap
        total = self.wallet.cash
        if snap is None:
            return total
        for position in self.wallet.positions:
            total += self._liquidation_value(position, snap)
        return total

    def snapshot_state(self, mark: MarketSnapshot | None = None) -> dict[str, Any]:
        with self._lock:
            if mark is not None:
                self.last_snap = mark
            snap = self.last_snap
            now = time.time()
            equity = self.equity(snap)
            remaining = max(0.0, self.wallet.started_at + self.wallet.horizon_s - now)
            stats = self.stats()
            return {
                "cash": self.wallet.cash,
                "equity": equity,
                "pnl": equity - START_CASH,
                "started_at": self.wallet.started_at,
                "remaining_s": remaining,
                "target": self.wallet.target,
                "halted": self.wallet.halted,
                "halt_reason": self.wallet.halt_reason,
                "frozen": now < self.wallet.frozen_until,
                "freeze_detail": self.wallet.freeze_detail,
                "positions": [self._position_view(position, snap) for position in self.wallet.positions],
                "log": list(self.wallet.log[-40:]),
                "lessons": list(self.wallet.lessons[-8:]),
                "closed_n": len(self.wallet.closed),
                "stats": stats,
                "doctrine": Doctrine(**self.wallet.doctrine.__dict__),
                "stand_down": self.wallet.doctrine.stand_down,
                "sample_from": self.wallet.sample_from,
            }

    def read_model(self) -> tuple[Doctrine, Stats, bool, str, bool]:
        with self._lock:
            now = time.time()
            frozen = now < self.wallet.frozen_until
            return (
                Doctrine(**self.wallet.doctrine.__dict__),
                self.stats(),
                frozen,
                self.wallet.freeze_detail,
                self.wallet.halted,
            )

    def halt(self) -> None:
        notes: list[str] = []
        with self._lock:
            self.wallet.halted = True
            self.wallet.halt_reason = "Ručno gašenje"
            if self.last_snap is not None:
                self._flatten(self.last_snap, "HALT")
            self._note("🛑 Hitno gašenje. Nema novih ulaza.", telegram=True)
            save_wallet(self.wallet)
            notes = list(self.pending_notes)
        for text in notes:
            notify(text)

    def resume(self) -> None:
        with self._lock:
            now = time.time()
            if now >= self.wallet.started_at + self.wallet.horizon_s:
                self._note("Rok izazova je prošao. Nastavak ne otvara nove ulaze.")
                save_wallet(self.wallet)
                return
            self.wallet.halted = False
            self.wallet.halt_reason = ""
            self._note("Motor nastavlja. Papirnati ulazi su opet dozvoljeni.")
            save_wallet(self.wallet)

    def reset(self) -> None:
        with self._lock:
            self.wallet = fresh_wallet()
            self._symbol_cooldown.clear()
            self._last_global_entry = 0.0
            self._note("Izazov resetiran. Kapital 200 €, rok 10 sati, dnevnik prazan.")
            save_wallet(self.wallet)

    def new_sample(self) -> None:
        with self._lock:
            self.wallet.sample_from = len(self.wallet.closed)
            self.wallet.doctrine.stand_down = False
            fresh = Doctrine()
            self.wallet.doctrine.kelly_fraction = fresh.kelly_fraction
            self.wallet.doctrine.kelly_cap = fresh.kelly_cap
            self.wallet.doctrine.prior_win = fresh.prior_win
            self._lesson("Novi uzorak. Kelly kreće od priora, stari trejdovi ne ulaze u formulu.")
            save_wallet(self.wallet)

    def _expire(self, now: float) -> None:
        if self.wallet.halted:
            return
        if now >= self.wallet.started_at + self.wallet.horizon_s:
            self.wallet.halted = True
            self.wallet.halt_reason = "Rok 10 sati je istekao"
            if self.last_snap is not None:
                self._flatten(self.last_snap, "ROK")
            self._note("⏱️ Rok istekao. Pozicije su zatvorene, novi ulazi stoje.", telegram=True)

    def _manage_all(self, snapshot: MarketSnapshot, frozen: bool) -> None:
        still_open: list[Position] = []
        for position in self.wallet.positions:
            if self._manage(position, snapshot, frozen):
                still_open.append(position)
        self.wallet.positions = still_open

    def _manage(self, position: Position, snapshot: MarketSnapshot, frozen: bool) -> bool:
        bid = _mark_bid(snapshot, position.symbol)
        if bid is None or position.qty <= 0 or position.entry <= 0:
            return True
        if bid > position.peak:
            position.peak = bid
        gain = (bid - position.entry) / position.entry
        if gain > position.mfe:
            position.mfe = gain
        doctrine = self.wallet.doctrine
        if frozen:
            position.sl = max(position.sl, position.entry)
        if position.mfe >= doctrine.be_trigger and position.sl < position.entry:
            position.sl = position.entry
            self._note(f"{position.symbol} stop dignut na ulaz. Rizik je nula.")
        if position.mfe >= doctrine.partial_trigger and not position.partial_done:
            before = position.realized
            qty = position.qty * doctrine.partial_frac
            self._sell(position, qty, bid, snapshot.books.get(position.symbol), "DIO")
            position.partial_done = True
            part = position.realized - before
            self._note(
                f"🎯 {position.symbol} djelomično {_fmt_eur(part)} "
                f"({int(doctrine.partial_frac * 100)}% na {_fmt_pct(position.mfe)}).",
                telegram=True,
            )
            if position.qty <= 0:
                return False
        bars = snapshot.candles.get(position.symbol, {}).get("15m", ())
        live_atr = atr_indicator(bars, doctrine.atr_period) if bars else None
        if live_atr:
            position.context["atr"] = live_atr
        atr_value = position.context.get("atr")
        if position.mfe >= doctrine.be_trigger and isinstance(atr_value, (int, float)) and atr_value > 0:
            trail = position.peak - doctrine.atr_mult * float(atr_value)
            if trail > position.sl:
                position.sl = trail
        if bid <= position.sl:
            reason = "BTC_FREEZE" if frozen and bid < position.entry else "SL"
            if position.sl > position.entry * 1.001:
                reason = "TRAIL"
            self._sell(position, position.qty, bid, snapshot.books.get(position.symbol), reason)
            return False
        return position.qty > 0

    def _maybe_enter(self, snapshot: MarketSnapshot, now: float, frozen: bool) -> None:
        if frozen or len(self.wallet.positions) >= self.wallet.doctrine.max_positions:
            return
        if now - self._last_global_entry < GLOBAL_ENTRY_GAP_S:
            return
        held = {position.symbol for position in self.wallet.positions}
        best = None
        for symbol in TRADABLE:
            if symbol in held:
                continue
            if now < self._symbol_cooldown.get(symbol, 0.0):
                continue
            decision = evaluate(
                snapshot,
                symbol,
                self.wallet.doctrine,
                self.stats(),
                frozen=False,
                halted=False,
            )
            if decision.setup and not decision.allow:
                self._symbol_cooldown[symbol] = now + 30.0
            if decision.allow and (best is None or decision.score > best.score):
                best = decision
        if best is None:
            return
        self._open(best, snapshot, now)

    def _open(self, decision, snapshot: MarketSnapshot, now: float) -> None:
        symbol = decision.symbol
        ask = _mark_ask(snapshot, symbol)
        if ask is None:
            return
        book = snapshot.books.get(symbol)
        slip = slippage(book, self.wallet.doctrine)
        fill = ask * (1.0 + slip)
        equity = self.equity(snapshot)
        fraction = min(decision.stake_fraction, self.wallet.doctrine.kelly_cap)
        stake = min(equity * fraction, self.wallet.cash * 0.92)
        if stake < MIN_STAKE_EUR:
            return
        fee_rate = self.wallet.doctrine.taker_fee
        fee = stake * fee_rate / (1.0 + fee_rate)
        notional = stake - fee
        qty = notional / fill
        if qty <= 0:
            return
        sl = fill * (1.0 - self.wallet.doctrine.sl_pct)
        tp = fill * (1.0 + self.wallet.doctrine.tp_pct)
        context = {
            "imbalance": decision.metrics.get("imbalance"),
            "veto_flags": list(decision.metrics.get("veto_flags") or []),
            "sentiment": decision.metrics.get("sentiment"),
            "rsi4h": decision.metrics.get("rsi4h"),
            "funding": decision.metrics.get("funding"),
            "atr": decision.metrics.get("atr"),
            "stake_fraction": fraction,
            "initial_cost": stake,
        }
        position = Position(
            symbol=symbol,
            qty=qty,
            entry=fill,
            sl=sl,
            tp=tp,
            opened_ms=int(now * 1000),
            fees=fee,
            cost=stake,
            peak=fill,
            mfe=0.0,
            partial_done=False,
            realized=0.0,
            initial_qty=qty,
            context=context,
        )
        self.wallet.cash -= stake
        self.wallet.positions.append(position)
        self.wallet.last_entry_at = now
        self._last_global_entry = now
        self._symbol_cooldown[symbol] = now + 15 * 60
        self._note(
            f"🎯 {symbol} long @ {_fmt_px(fill)} · ulog {_fmt_eur(stake)} · "
            f"SL {_fmt_px(sl)} · TP {_fmt_px(tp)} · naknada {_fmt_eur(fee)}",
            telegram=True,
        )

    def _sell(self, position: Position, qty: float, price: float, book: BookTop | None, reason: str) -> None:
        qty = min(qty, position.qty)
        if qty <= 0 or position.qty <= 0:
            return
        slip = slippage(book, self.wallet.doctrine)
        fill = price * (1.0 - slip)
        notional = fill * qty
        fee = notional * self.wallet.doctrine.taker_fee
        proceeds = notional - fee
        unit = position.cost / position.qty
        basis = unit * qty
        pnl = proceeds - basis
        position.realized += pnl
        position.fees += fee
        position.cost -= basis
        position.qty -= qty
        self.wallet.cash += proceeds
        closed_all = position.qty <= 1e-12
        if closed_all:
            position.qty = 0.0
            self._archive(position, fill, reason)

    def _flatten(self, snapshot: MarketSnapshot, reason: str) -> None:
        for position in list(self.wallet.positions):
            bid = _mark_bid(snapshot, position.symbol)
            if bid is None:
                continue
            self._sell(position, position.qty, bid, snapshot.books.get(position.symbol), reason)
        self.wallet.positions = [position for position in self.wallet.positions if position.qty > 0]

    def _archive(self, position: Position, exit_price: float, reason: str) -> None:
        pnl = position.realized
        initial = float(position.context.get("initial_cost") or 0.0)
        if initial <= 0:
            initial = position.initial_qty * position.entry * (1.0 + self.wallet.doctrine.taker_fee)
        pnl_pct = pnl / initial if initial else 0.0
        trade = {
            "symbol": position.symbol,
            "entry": position.entry,
            "exit": exit_price,
            "pnl": round(pnl, 4),
            "pnl_pct": round(pnl_pct, 6),
            "fees": round(position.fees, 4),
            "mfe": round(position.mfe, 6),
            "reason": reason,
            "opened_ms": position.opened_ms,
            "closed_ms": int(time.time() * 1000),
            "context": {
                "imbalance": position.context.get("imbalance"),
                "veto_flags": position.context.get("veto_flags") or [],
                "sentiment": position.context.get("sentiment"),
            },
        }
        self.wallet.closed.append(trade)
        self.wallet.closed = self.wallet.closed[-500:]
        sign = "+" if pnl >= 0 else ""
        self._note(
            f"{'✅' if pnl >= 0 else '❌'} {position.symbol} zatvoren {reason} · {sign}{_fmt_eur(pnl)}",
            telegram=True,
        )
        stats = self.stats()
        if stats.avg_loss > 0:
            payoff = stats.avg_win / stats.avg_loss
        elif stats.wins > 0:
            payoff = 5.0
        else:
            payoff = 0.0
        lessons = self.teacher.review_close(
            self.wallet.doctrine,
            pnl=pnl,
            mfe=position.mfe,
            pnl_pct=pnl_pct,
            context=position.context,
            stats_n=stats.n,
            win_rate=stats.win_rate,
            payoff=payoff,
        )
        for lesson in lessons:
            self._lesson(lesson)
        self.teacher.queue_remote(self.wallet.doctrine, self.wallet.closed[self.wallet.sample_from :])

    def _liquidation_value(self, position: Position, snapshot: MarketSnapshot) -> float:
        bid = _mark_bid(snapshot, position.symbol)
        if bid is None:
            return 0.0
        book = snapshot.books.get(position.symbol)
        slip = slippage(book, self.wallet.doctrine)
        gross = bid * (1.0 - slip) * position.qty
        fee = gross * self.wallet.doctrine.taker_fee
        return max(0.0, gross - fee)

    def _mark_equity(self, snapshot: MarketSnapshot, now: float) -> None:
        if now - self._last_equity_mark < 10:
            return
        self._last_equity_mark = now
        self.wallet.equity.append({"t": now, "v": round(self.equity(snapshot), 4)})
        self.wallet.equity = self.wallet.equity[-2000:]

    def _position_view(self, position: Position, snapshot: MarketSnapshot | None) -> dict[str, Any]:
        bid = _mark_bid(snapshot, position.symbol) if snapshot else None
        live = (bid - position.entry) / position.entry if bid else 0.0
        return {
            "symbol": position.symbol,
            "qty": position.qty,
            "entry": position.entry,
            "sl": position.sl,
            "tp": position.tp,
            "mfe": position.mfe,
            "live_pct": live,
            "partial_done": position.partial_done,
            "fees": position.fees,
            "realized": position.realized,
            "note": self._trail_note(position),
        }

    def _trail_note(self, position: Position) -> str:
        if position.partial_done and position.sl > position.entry:
            return f"50% u džepu. Trail SL {_fmt_px(position.sl)}."
        if position.sl >= position.entry * 0.999:
            return "Breakeven postavljen. Čekam +5% za pola pozicije."
        return f"Početni SL {_fmt_px(position.sl)} · TP {_fmt_px(position.tp)}."

    def _note(self, text: str, telegram: bool = False) -> None:
        self.wallet.log.append({"t": time.time(), "text": text})
        self.wallet.log = self.wallet.log[-200:]
        if telegram:
            self.pending_notes.append(text)

    def _lesson(self, text: str) -> None:
        stamp = "🧬 " + text
        self.wallet.lessons.append(stamp)
        self.wallet.lessons = self.wallet.lessons[-30:]
        self._note("Učitelj: " + text)

    def _apply_remote(self) -> None:
        for lesson in self.teacher.pull_remote(self.wallet.doctrine):
            self._lesson(lesson)

    def trail_note_for(self, symbol: str) -> str:
        with self._lock:
            for position in self.wallet.positions:
                if position.symbol == symbol:
                    return self._trail_note(position)
        return ""


def _fmt_eur(value: float) -> str:
    text = f"{value:,.2f}"
    return text.replace(",", " ").replace(".", ",") + " €"


def _fmt_px(value: float) -> str:
    digits = 4 if value < 20 else 2
    text = f"{value:,.{digits}f}"
    return text.replace(",", " ").replace(".", ",")


def _fmt_pct(value: float) -> str:
    text = f"{value * 100:,.2f}"
    return text.replace(",", " ").replace(".", ",") + "%"
