"""Zajednički tipovi. Svijeće i knjiga su nepromjenjivi da tick nema race."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Candle:
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class BookTop:
    bids: tuple[tuple[float, float], ...]
    asks: tuple[tuple[float, float], ...]
    levels: int
    synced: bool

    @property
    def bid(self) -> float | None:
        return self.bids[0][0] if self.bids else None

    @property
    def ask(self) -> float | None:
        return self.asks[0][0] if self.asks else None

    @property
    def spread(self) -> float | None:
        if self.bid is None or self.ask is None or self.ask <= 0:
            return None
        return (self.ask - self.bid) / self.ask


@dataclass(frozen=True)
class MarketSnapshot:
    now_ms: int
    books: dict[str, BookTop]
    candles: dict[str, dict[str, tuple[Candle, ...]]]
    forming: dict[str, dict[str, Candle]]
    live: dict[str, float]
    funding: dict[str, float]
    hub_status: str
    hub_error: str
    ready: bool


@dataclass(frozen=True)
class AgentView:
    id: str
    state: str
    kicker: str
    title: str
    value: str
    detail: str


@dataclass
class Doctrine:
    """Živi parametri. Učitelj ih miče samo unutar tvrdog raspona."""

    whale_min: float = 0.50
    whale_block: float = 0.40
    blitz: bool = True
    blitz_floor: float = 0.04
    leverage: float = 5.0
    pace: float = 1.0
    whale_boost: float = 1.25
    btc_drop: float = 0.007
    btc_vol_mult: float = 3.0
    btc_window: int = 3
    skeptic_flags: int = 2
    rsi_veto: float = 65.0
    funding_veto: float = 0.0005
    atr_period: int = 14
    atr_mult: float = 1.2
    be_trigger: float = 0.003
    partial_trigger: float = 0.006
    partial_frac: float = 0.7
    sl_pct: float = 0.004
    tp_pct: float = 0.010
    kelly_fraction: float = 0.5
    kelly_cap: float = 0.55
    sentiment_boost: float = 1.5
    mtf_rsi_low: float = 40.0
    mtf_rsi_high: float = 55.0
    taker_fee: float = 0.001
    impact_bps: float = 0.0004
    prior_win: float = 0.52
    prior_payoff: float = 1.40
    min_trades: int = 10
    max_positions: int = 8
    max_spread: float = 0.0015
    stand_down: bool = False

    def clamped(self) -> Doctrine:
        limits = {
            "whale_min": (0.48, 0.85),
            "blitz_floor": (0.03, 0.40),
            "leverage": (1.0, 12.0),
            "whale_block": (0.25, 0.50),
            "whale_boost": (1.0, 1.40),
            "btc_drop": (0.004, 0.015),
            "btc_vol_mult": (2.0, 5.0),
            "skeptic_flags": (1, 3),
            "rsi_veto": (55.0, 75.0),
            "funding_veto": (0.0002, 0.0015),
            "atr_mult": (1.2, 3.5),
            "kelly_fraction": (0.15, 0.50),
            "kelly_cap": (0.08, 0.60),
            "sentiment_boost": (1.0, 1.50),
            "mtf_rsi_low": (35.0, 48.0),
            "mtf_rsi_high": (50.0, 62.0),
            "sl_pct": (0.004, 0.03),
            "tp_pct": (0.01, 0.08),
        }
        data = dict(self.__dict__)
        for key, (low, high) in limits.items():
            value = data[key]
            data[key] = max(low, min(high, value))
        data["stand_down"] = bool(data["stand_down"])
        data["blitz"] = bool(data.get("blitz", True))
        data["skeptic_flags"] = int(round(data["skeptic_flags"]))
        return Doctrine(**data)


@dataclass
class Stats:
    n: int = 0
    wins: int = 0
    losses: int = 0
    avg_win: float = 0.0
    avg_loss: float = 0.0

    @property
    def win_rate(self) -> float:
        return self.wins / self.n if self.n else 0.0


@dataclass
class Decision:
    symbol: str
    allow: bool
    reason: str
    stake_fraction: float
    score: float
    setup: bool
    views: tuple[AgentView, ...]
    metrics: dict = field(default_factory=dict)


def empty_snapshot() -> MarketSnapshot:
    return MarketSnapshot(
        now_ms=0,
        books={},
        candles={},
        forming={},
        live={},
        funding={},
        hub_status="BOOT",
        hub_error="",
        ready=False,
    )
