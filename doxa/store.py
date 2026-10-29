"""Novčanik na disku. Jedan JSON, atomarna zamjena, da se datoteka ne raspadne."""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from doxa.brains import Brain, default_brains, restore_brains
from doxa.config import HORIZON_S, MISSION_ID, START_CASH, TARGET_CASH, WALLET_PATH
from doxa.types import Doctrine


@dataclass
class Position:
    symbol: str
    qty: float
    entry: float
    sl: float
    tp: float
    opened_ms: int
    fees: float
    cost: float
    peak: float
    mfe: float
    partial_done: bool
    realized: float
    initial_qty: float
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class Wallet:
    cash: float
    started_at: float
    horizon_s: float
    target: float
    positions: list[Position]
    closed: list[dict[str, Any]]
    equity: list[dict[str, float]]
    log: list[dict[str, Any]]
    halted: bool
    halt_reason: str
    lessons: list[str]
    sample_from: int
    last_relax_at: float
    last_entry_at: float
    frozen_until: float
    freeze_detail: str
    doctrine: Doctrine
    mission: str
    brains: dict[str, Brain]
    pack: int


def fresh_wallet(now: float | None = None) -> Wallet:
    clock = time.time() if now is None else now
    return Wallet(
        cash=START_CASH,
        started_at=clock,
        horizon_s=HORIZON_S,
        target=TARGET_CASH,
        positions=[],
        closed=[],
        equity=[{"t": clock, "v": START_CASH}],
        log=[],
        halted=False,
        halt_reason="",
        lessons=[
            "Naredba: 200 € u 1.000 € za 60 minuta. Ako rok istekne, ured se zatvara.",
            "Svaki agent ima vlastiti mozak. Uči iz svakog zatvaranja i sam miče prag.",
        ],
        sample_from=0,
        last_relax_at=clock,
        last_entry_at=clock,
        frozen_until=0.0,
        freeze_detail="",
        doctrine=Doctrine(),
        mission=MISSION_ID,
        brains=default_brains(),
        pack=2,
    )


def _position_from(raw: dict[str, Any]) -> Position:
    base = Position(
        symbol=str(raw.get("symbol", "")),
        qty=float(raw.get("qty", 0)),
        entry=float(raw.get("entry", 0)),
        sl=float(raw.get("sl", 0)),
        tp=float(raw.get("tp", 0)),
        opened_ms=int(raw.get("opened_ms", 0)),
        fees=float(raw.get("fees", 0)),
        cost=float(raw.get("cost", 0)),
        peak=float(raw.get("peak", 0)),
        mfe=float(raw.get("mfe", 0)),
        partial_done=bool(raw.get("partial_done", False)),
        realized=float(raw.get("realized", 0)),
        initial_qty=float(raw.get("initial_qty", raw.get("qty", 0))),
        context=dict(raw.get("context") or {}),
    )
    return base


def wallet_from_dict(raw: dict[str, Any]) -> Wallet:
    doctrine_raw = dict(raw.get("doctrine") or {})
    known = {key: doctrine_raw[key] for key in Doctrine.__dataclass_fields__ if key in doctrine_raw}
    doctrine = Doctrine(**known).clamped()
    wallet = fresh_wallet(float(raw.get("started_at", time.time())))
    wallet.cash = float(raw.get("cash", START_CASH))
    wallet.horizon_s = float(raw.get("horizon_s", HORIZON_S))
    wallet.target = float(raw.get("target", TARGET_CASH))
    wallet.positions = [_position_from(item) for item in raw.get("positions") or []]
    wallet.closed = list(raw.get("closed") or [])
    wallet.equity = list(raw.get("equity") or [])
    wallet.log = list(raw.get("log") or [])
    wallet.halted = bool(raw.get("halted", False))
    wallet.halt_reason = str(raw.get("halt_reason") or "")
    wallet.lessons = [str(item) for item in (raw.get("lessons") or wallet.lessons)]
    wallet.sample_from = int(raw.get("sample_from", 0))
    wallet.last_relax_at = float(raw.get("last_relax_at", wallet.started_at))
    wallet.last_entry_at = float(raw.get("last_entry_at", wallet.started_at))
    wallet.frozen_until = float(raw.get("frozen_until", 0))
    wallet.freeze_detail = str(raw.get("freeze_detail") or "")
    wallet.doctrine = doctrine
    wallet.mission = str(raw.get("mission") or "")
    wallet.brains = restore_brains(raw.get("brains"))
    wallet.pack = int(raw.get("pack") or 1)
    if wallet.pack < 2:
        _upgrade_pack(wallet.doctrine)
        wallet.pack = 2
    return wallet


def _upgrade_pack(doctrine: Doctrine) -> None:
    """Stari sat drži prevelik ulog za jato. Jednom ga rastavi na više brzih ulaza."""
    doctrine.max_positions = max(8, int(doctrine.max_positions))
    doctrine.blitz_floor = min(float(doctrine.blitz_floor), 0.12)
    doctrine.tp_pct = min(float(doctrine.tp_pct), 0.012)
    doctrine.sl_pct = min(float(doctrine.sl_pct), 0.005)
    doctrine.be_trigger = min(float(doctrine.be_trigger), 0.0045)
    doctrine.partial_trigger = min(float(doctrine.partial_trigger), 0.007)
    doctrine.atr_mult = min(float(doctrine.atr_mult), 1.3)
    doctrine.partial_frac = max(float(doctrine.partial_frac), 0.65)
    doctrine.__dict__.update(doctrine.clamped().__dict__)


def wallet_to_dict(wallet: Wallet) -> dict[str, Any]:
    payload = asdict(wallet)
    payload["doctrine"] = asdict(wallet.doctrine)
    return payload


def wallet_path() -> Path:
    override = os.getenv("DOXA_WALLET", "").strip()
    return Path(override or WALLET_PATH)


def peek_wallet() -> Wallet | None:
    path = wallet_path()
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict) or str(raw.get("mission") or "") != MISSION_ID:
        return fresh_wallet()
    return wallet_from_dict(raw)


def load_wallet() -> Wallet:
    path = wallet_path()
    if not path.exists():
        wallet = fresh_wallet()
        save_wallet(wallet)
        return wallet
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        wallet = fresh_wallet()
        save_wallet(wallet)
        return wallet
    if not isinstance(raw, dict) or str(raw.get("mission") or "") != MISSION_ID:
        wallet = fresh_wallet()
        save_wallet(wallet)
        return wallet
    return wallet_from_dict(raw)


def save_wallet(wallet: Wallet) -> None:
    path = wallet_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(wallet_to_dict(wallet), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    os.replace(temporary, path)
