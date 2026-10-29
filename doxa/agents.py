"""Sedam agenata. Svaki ima vlastiti mozak; ulaz ide kad se jato složi."""

from __future__ import annotations

from doxa.brains import Brain, default_brains, tune
from doxa.config import GUARD_SYMBOL
from doxa.indicators import (
    atr,
    bullish_engulfing,
    closes,
    ema,
    fractional_kelly,
    order_book_imbalance,
    rsi,
    volume_divergence,
)
from doxa.types import AgentView, BookTop, Candle, Decision, Doctrine, MarketSnapshot, Stats


def _fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "—"
    text = f"{value:,.{digits}f}"
    return text.replace(",", " ").replace(".", ",")


def _pct(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "—"
    return _fmt(value * 100.0, digits) + "%"


def _bars(snapshot: MarketSnapshot, symbol: str, interval: str) -> tuple[Candle, ...]:
    return snapshot.candles.get(symbol, {}).get(interval, ())


def _book(snapshot: MarketSnapshot, symbol: str) -> BookTop | None:
    return snapshot.books.get(symbol)


def assess_btc(snapshot: MarketSnapshot, doctrine: Doctrine) -> tuple[bool, float | None, float | None, str]:
    """Pad BTC-a u prozoru od N minuta uz volumen iznad praga."""
    candles = _bars(snapshot, GUARD_SYMBOL, "1m")
    window = max(2, int(doctrine.btc_window))
    if len(candles) < window + 15:
        return False, None, None, "Čekam 1m tok BTC-a."
    start = candles[-1 - window].close
    end = candles[-1].close
    if start <= 0:
        return False, None, None, "BTC cijena nije valjana."
    delta = (end - start) / start
    recent_volume = sum(candle.volume for candle in candles[-window:])
    blocks: list[float] = []
    history = candles[:-window]
    for index in range(0, len(history) - window + 1):
        blocks.append(sum(candle.volume for candle in history[index : index + window]))
    baseline = sum(blocks[-30:]) / len(blocks[-30:]) if blocks else 0.0
    ratio = (recent_volume / baseline) if baseline > 0 else 0.0
    triggered = delta <= -doctrine.btc_drop and ratio >= doctrine.btc_vol_mult
    detail = f"Δ {_pct(delta)} · volumen { _fmt(ratio, 1)}× prosjeka"
    if triggered:
        detail = "EMERGENCY FREEZE · " + detail
    return triggered, delta, ratio, detail


def _sentiment(rsi15: float | None, imbalance: float | None, ret_15: float | None, funding: float | None) -> tuple[str, int, str]:
    """Brzi lokalni radar. Nema izmišljenih objava; hrani se cijenom, knjigom i fundingom."""
    score = 50
    if ret_15 is not None:
        score += max(-25, min(25, ret_15 * 800))
    if imbalance is not None:
        score += (imbalance - 0.5) * 80
    if rsi15 is not None:
        score += (rsi15 - 50) * 0.4
    if funding is not None and funding > 0.0004:
        score -= 8
    score = int(max(0, min(100, round(score))))
    if score >= 78 and (imbalance or 0) >= 0.62 and (ret_15 or 0) > 0.004:
        label = "EXTREME_HYPE"
        action = "BOOST_STAKE"
    elif score >= 62 and (ret_15 or 0) > 0:
        label = "HYPE"
        action = "HOLD_STAKE"
    elif score <= 35:
        label = "FEAR"
        action = "CUT_STAKE"
    else:
        label = "NEUTRAL"
        action = "HOLD_STAKE"
    return label, score, action


def _stake(doctrine: Doctrine, stats: Stats, imbalance: float | None, sentiment: str) -> tuple[float, str]:
    if stats.n >= doctrine.min_trades and stats.avg_loss > 0 and stats.wins + stats.losses > 0:
        payoff = min(5.0, stats.avg_win / stats.avg_loss) if stats.avg_loss else doctrine.prior_payoff
        win_rate = stats.win_rate
        source = f"uzorak {stats.n}"
    else:
        payoff = doctrine.prior_payoff
        win_rate = doctrine.prior_win
        source = f"prior do {doctrine.min_trades}. trejda"
    base = fractional_kelly(win_rate, payoff, doctrine.kelly_fraction, doctrine.kelly_cap)
    boost = 1.0
    notes: list[str] = []
    if imbalance is not None and imbalance >= doctrine.whale_min:
        boost *= doctrine.whale_boost
        notes.append("kit")
    if sentiment == "EXTREME_HYPE":
        boost *= doctrine.sentiment_boost
        notes.append("radar")
    if sentiment == "FEAR":
        boost *= 0.7
        notes.append("strah")
    sized = min(doctrine.kelly_cap, base * boost)
    if doctrine.blitz and not doctrine.stand_down:
        floor = min(doctrine.blitz_floor, doctrine.kelly_cap)
        if sized < floor:
            sized = floor
            notes.append("naredba")
    extra = (" · " + "+".join(notes)) if notes else ""
    text = f"f {_pct(sized, 1)} · p {_pct(win_rate, 0)} · b {_fmt(payoff, 2)} · {source}{extra}"
    return sized, text


def _mind(brain: Brain, features: list[float]) -> tuple[str, bool, float]:
    yes, probability = brain.vote(features)
    mark = "DA" if yes else "NE"
    text = f" Mozak {mark} {_pct(probability, 0)} · {brain.seen} naučenih · gen {brain.generation}."
    return text, yes, probability


def evaluate(
    snapshot: MarketSnapshot,
    symbol: str,
    doctrine: Doctrine,
    stats: Stats,
    *,
    frozen: bool = False,
    freeze_detail: str = "",
    halted: bool = False,
    position_note: str = "",
    brains: dict[str, Brain] | None = None,
) -> Decision:
    """Jedan prolaz kroz svih 7 agenata za jedan simbol."""
    doctrine = doctrine.clamped()
    minds = brains if brains is not None else default_brains()
    tune(doctrine, minds)
    c1 = _bars(snapshot, symbol, "1m")
    c15 = _bars(snapshot, symbol, "15m")
    c1h = _bars(snapshot, symbol, "1h")
    c4h = _bars(snapshot, symbol, "4h")
    book = _book(snapshot, symbol)
    funding = snapshot.funding.get(symbol)

    px1 = closes(c1)
    px15 = closes(c15)
    px1h = closes(c1h)
    px4h = closes(c4h)
    rsi15 = rsi(px15, 14)
    rsi15_prev = rsi(px15[:-1], 14) if len(px15) > 20 else None
    rsi1h = rsi(px1h, 14)
    rsi1h_prev = rsi(px1h[:-1], 14) if len(px1h) > 20 else None
    rsi4h = rsi(px4h, 14)
    ema9 = ema(px15, 9)
    ema50 = ema(px4h, 50)
    atr15 = atr(c15, doctrine.atr_period)

    imbalance = None
    spread = None
    if book and book.bids and book.asks:
        imbalance = order_book_imbalance(book.bids, book.asks)
        spread = book.spread

    ret15 = None
    if len(c15) >= 2 and c15[-2].close > 0:
        ret15 = (c15[-1].close - c15[-2].close) / c15[-2].close

    label, velocity, action = _sentiment(rsi15, imbalance, ret15, funding)
    stake, stake_text = _stake(doctrine, stats, imbalance, label)

    # --- 1 Whale ---
    if imbalance is None:
        whale_state, whale_value, whale_detail = "idle", "—", "Knjiga još nije usklađena."
    elif imbalance >= doctrine.whale_min:
        whale_state = "hot"
        whale_value = _pct(imbalance, 0)
        whale_detail = f"Bid zid {_pct(imbalance, 1)}. Snajper spreman."
    elif imbalance <= doctrine.whale_block:
        whale_state = "block"
        whale_value = _pct(imbalance, 0)
        whale_detail = f"Ask zid {_pct(1 - imbalance, 1)}. Ulaz zabranjen."
    else:
        whale_state = "armed"
        whale_value = _pct(imbalance, 0)
        whale_detail = f"Knjiga {_pct(imbalance, 1)}. Ispod praga {_pct(doctrine.whale_min, 0)}."

    # --- 2 BTC guard ---
    triggered, delta, ratio, guard_text = assess_btc(snapshot, doctrine)
    if frozen:
        guard_state = "freeze"
        guard_value = _pct(delta, 2) if delta is not None else "STOP"
        guard_detail = freeze_detail or "Zamrzavanje aktivno. Nema novih kupnji."
    elif triggered:
        guard_state = "freeze"
        guard_value = _pct(delta, 2)
        guard_detail = guard_text
    else:
        guard_state = "armed"
        guard_value = _pct(delta, 2) if delta is not None else "—"
        guard_detail = guard_text

    # --- 6 MTF. Blitz koristi zatvorenu 1m svijeću čim tok postoji. ---
    ema21 = ema(px15, 21)
    ema9_1 = ema(px1, 9)
    rsi1 = rsi(px1, 14)
    rsi1_prev = rsi(px1[:-1], 14) if len(px1) > 20 else None
    fast = doctrine.blitz and len(c1) >= 30 and ema21 is not None
    missing = []
    if fast:
        if len(c15) < 21:
            missing.append("15m")
        tide = len(c15) > 0 and ema21 is not None and c15[-1].close > ema21
        wave = True
        hook = (
            ema9_1 is not None
            and rsi1 is not None
            and rsi1_prev is not None
            and c1[-1].close > ema9_1
            and rsi1 > rsi1_prev
            and 45.0 <= rsi1 <= 74.0
        )
        turn = bullish_engulfing(c1) or hook
        mtf_ok = tide and turn and not missing
    else:
        if ema50 is None:
            missing.append("4h")
        if rsi1h is None:
            missing.append("1h")
        if len(c15) < 20 or ema9 is None or rsi15 is None:
            missing.append("15m")
        tide = ema50 is not None and len(c4h) > 0 and c4h[-1].close > ema50
        wave = (
            rsi1h is not None
            and rsi1h_prev is not None
            and doctrine.mtf_rsi_low <= rsi1h <= doctrine.mtf_rsi_high
            and rsi1h < rsi1h_prev
        )
        hook = (
            ema9 is not None
            and rsi15 is not None
            and rsi15_prev is not None
            and len(c15) > 0
            and c15[-1].close > ema9
            and rsi15 > rsi15_prev
            and 48.0 <= rsi15 <= 68.0
        )
        turn = bullish_engulfing(c15) or hook
        mtf_ok = tide and wave and turn and not missing
    if missing:
        mtf_state, mtf_value = "idle", "—"
        mtf_detail = "Čekam svijeće: " + ", ".join(missing) + "."
    elif mtf_ok and fast:
        mtf_state, mtf_value = "hot", "1m"
        mtf_detail = f"Blitz: 15m iznad EMA21 · 1m RSI {_fmt(rsi1, 1)} okret."
    elif mtf_ok:
        mtf_state, mtf_value = "hot", "3/3"
        mtf_detail = f"4h iznad EMA50 · 1h RSI {_fmt(rsi1h, 1)} pada · 15m okret."
    elif fast:
        lights = f"{'●' if tide else '○'}15m {'●' if turn else '○'}1m"
        mtf_state, mtf_value = "armed", lights
        mtf_detail = f"RSI 1m {_fmt(rsi1, 1)} · RSI 15m {_fmt(rsi15, 1)}. Čekam oba zelena."
    else:
        lights = f"{'●' if tide else '○'}4h {'●' if wave else '○'}1h {'●' if turn else '○'}15m"
        mtf_state, mtf_value = "armed", lights
        mtf_detail = (
            f"RSI15 {_fmt(rsi15, 1)} · RSI1h {_fmt(rsi1h, 1)} · RSI4h {_fmt(rsi4h, 1)}. "
            "Nema ulaza bez tri zelena."
        )

    # --- 3 Skeptik ---
    flags: list[str] = []
    if mtf_ok:
        if volume_divergence(c1 if fast else c15):
            flags.append("volumen divergira")
        if funding is not None and funding > doctrine.funding_veto:
            flags.append(f"funding OKX {_pct(funding, 3)}")
        hot_rsi = rsi15 if fast else rsi4h
        hot_label = "RSI 15m" if fast else "RSI 4h"
        if hot_rsi is not None and hot_rsi > doctrine.rsi_veto:
            flags.append(f"{hot_label} {_fmt(hot_rsi, 1)}")
    veto = mtf_ok and len(flags) >= doctrine.skeptic_flags
    if not mtf_ok:
        skeptic_state, skeptic_value = "idle", "—"
        skeptic_detail = "Nema prijedloga za oboriti."
    elif veto:
        skeptic_state, skeptic_value = "veto", f"{len(flags)}/{doctrine.skeptic_flags}"
        skeptic_detail = "VETO · " + " · ".join(flags)
    elif flags:
        skeptic_state, skeptic_value = "armed", f"{len(flags)}/{doctrine.skeptic_flags}"
        skeptic_detail = "Jedna zastavica nije veto: " + " · ".join(flags)
    else:
        skeptic_state, skeptic_value = "armed", "0"
        funding_txt = _pct(funding, 3) if funding is not None else "nema"
        skeptic_detail = f"Čisto. Funding OKX {funding_txt}. RSI 4h {_fmt(rsi4h, 1)}."

    # --- 4 Trail ---
    if position_note:
        trail_state, trail_value = "hot", "U POZICIJI"
        trail_detail = position_note
    else:
        trail_state, trail_value = "armed", f"{_fmt(doctrine.atr_mult, 1)}×ATR"
        trail_detail = (
            f"SL −{_fmt(doctrine.sl_pct * 100, 1)}%. "
            f"Na +{_fmt(doctrine.be_trigger * 100, 1)}% breakeven, "
            f"na +{_fmt(doctrine.partial_trigger * 100, 1)}% zatvaram {int(doctrine.partial_frac * 100)}%, "
            f"ostatak {_fmt(doctrine.atr_mult, 1)}×ATR. Poluga { _fmt(doctrine.leverage, 0)}×."
        )

    # --- 5 Radar ---
    if label == "EXTREME_HYPE":
        radar_state = "boost"
    elif label == "FEAR":
        radar_state = "block"
    else:
        radar_state = "armed"
    radar_detail = f'{{"sentiment":"{label}","velocity":{velocity},"action":"{action}"}}'

    # --- 7 Kelly ---
    if doctrine.stand_down:
        kelly_state, kelly_value = "block", "STOP"
        kelly_detail = "Učitelj je ugasio ulog. Rub uzorka je negativan."
    elif stake <= 0:
        kelly_state, kelly_value = "block", "0%"
        kelly_detail = "Kelly je nula. Nema matematičkog uloga. " + stake_text
    else:
        kelly_state, kelly_value = "armed", _pct(stake, 1)
        kelly_detail = stake_text

    imbalance_x = 0.0 if imbalance is None else float(imbalance)
    whale_note, whale_yes, whale_p = _mind(
        minds["whale"],
        [
            imbalance_x,
            1.0 if imbalance is not None and imbalance >= doctrine.whale_min else 0.0,
            1.0 if spread is None or spread <= doctrine.max_spread else 0.0,
            1.0,
        ],
    )
    guard_note, _guard_yes, guard_p = _mind(
        minds["guard"],
        [
            1.0 if delta is not None and delta > -doctrine.btc_drop else 0.0,
            0.0 if triggered else 1.0,
            0.5 if ratio is None else max(0.0, min(1.0, 1.0 - ratio / 6.0)),
            1.0,
        ],
    )
    mtf_note, mtf_yes, mtf_p = _mind(
        minds["mtf"],
        [
            1.0 if tide else 0.0,
            1.0 if turn else 0.0,
            1.0 if wave or fast else 0.0,
            0.0 if missing else 1.0,
        ],
    )
    if mtf_ok:
        skeptic_features = [
            0.0 if veto else 1.0,
            max(0.0, 1.0 - len(flags) / 2.0),
            1.0 if funding is None or funding <= doctrine.funding_veto else 0.0,
            0.0 if any("RSI" in flag for flag in flags) else 1.0,
        ]
    else:
        skeptic_features = [0.2, 0.2, 0.5, 0.2]
    skeptic_note, skeptic_yes, skeptic_p = _mind(minds["skeptic"], skeptic_features)
    trail_note, trail_yes, trail_p = _mind(
        minds["trail"],
        [1.0, 1.0, 0.4 if position_note else 1.0, 1.0],
    )
    radar_note, radar_yes, radar_p = _mind(
        minds["radar"],
        [
            velocity / 100.0,
            0.0 if label == "FEAR" else 1.0,
            1.0 if label in {"HYPE", "EXTREME_HYPE"} else 0.45,
            1.0 if (ret15 or 0) > 0 else 0.3,
        ],
    )
    kelly_note, kelly_yes, kelly_p = _mind(
        minds["kelly"],
        [
            1.0 if stake > 0 else 0.0,
            max(0.0, min(1.0, stake / 0.25)),
            0.0 if doctrine.stand_down else 1.0,
            1.0,
        ],
    )
    whale_detail += whale_note
    guard_detail += guard_note
    mtf_detail += mtf_note
    skeptic_detail += skeptic_note
    trail_detail += trail_note
    radar_detail += radar_note
    kelly_detail += kelly_note
    mind_pack = {
        "whale": (whale_yes, whale_p),
        "guard": (_guard_yes, guard_p),
        "mtf": (mtf_yes, mtf_p),
        "skeptic": (skeptic_yes, skeptic_p),
        "trail": (trail_yes, trail_p),
        "radar": (radar_yes, radar_p),
        "kelly": (kelly_yes, kelly_p),
    }

    views = (
        AgentView("whale", whale_state, "L2", "WHALE", whale_value, whale_detail),
        AgentView("guard", guard_state, "BTC", "GUARD", guard_value, guard_detail),
        AgentView("skeptic", skeptic_state, "VETO", "SKEPTIK", skeptic_value, skeptic_detail),
        AgentView("trail", trail_state, "ATR", "TRAIL", trail_value, trail_detail),
        AgentView("radar", radar_state, "NLP", "RADAR", str(velocity), radar_detail),
        AgentView("mtf", mtf_state, "3 TF", "MTF", mtf_value, mtf_detail),
        AgentView("kelly", kelly_state, "f*", "KELLY", kelly_value, kelly_detail),
    )

    metrics = {
        "rsi15": rsi15,
        "rsi1h": rsi1h,
        "rsi4h": rsi4h,
        "ema9": ema9,
        "ema50": ema50,
        "atr": atr15,
        "imbalance": imbalance,
        "spread": spread,
        "funding": funding,
        "sentiment": label,
        "velocity": velocity,
        "veto_flags": flags,
        "stake": stake,
        "btc_delta": delta,
        "btc_vol_ratio": ratio,
        "tide": tide,
        "wave": wave,
        "turn": turn,
        "brains": {
            "whale": {
                "x": [
                    imbalance_x,
                    1.0 if imbalance is not None and imbalance >= doctrine.whale_min else 0.0,
                    1.0 if spread is None or spread <= doctrine.max_spread else 0.0,
                    1.0,
                ],
                "p": whale_p,
                "yes": whale_yes,
            },
            "guard": {
                "x": [
                    1.0 if delta is not None and delta > -doctrine.btc_drop else 0.0,
                    0.0 if triggered else 1.0,
                    0.5 if ratio is None else max(0.0, min(1.0, 1.0 - ratio / 6.0)),
                    1.0,
                ],
                "p": guard_p,
                "yes": _guard_yes,
            },
            "mtf": {
                "x": [1.0 if tide else 0.0, 1.0 if turn else 0.0, 1.0 if wave or fast else 0.0, 0.0 if missing else 1.0],
                "p": mtf_p,
                "yes": mtf_yes,
            },
            "skeptic": {"x": skeptic_features, "p": skeptic_p, "yes": skeptic_yes},
            "trail": {"x": [1.0, 1.0, 0.4 if position_note else 1.0, 1.0], "p": trail_p, "yes": trail_yes},
            "radar": {
                "x": [
                    velocity / 100.0,
                    0.0 if label == "FEAR" else 1.0,
                    1.0 if label in {"HYPE", "EXTREME_HYPE"} else 0.45,
                    1.0 if (ret15 or 0) > 0 else 0.3,
                ],
                "p": radar_p,
                "yes": radar_yes,
            },
            "kelly": {
                "x": [
                    1.0 if stake > 0 else 0.0,
                    max(0.0, min(1.0, stake / 0.25)),
                    0.0 if doctrine.stand_down else 1.0,
                    1.0,
                ],
                "p": kelly_p,
                "yes": kelly_yes,
            },
        },
    }

    pack_names = ("whale", "mtf", "skeptic", "radar", "kelly", "trail")
    pack_yes = [name for name in pack_names if mind_pack[name][0]]
    reason = "Nema setupa."
    allow = False
    setup = bool(mtf_ok or (mtf_yes and whale_yes))
    score = 0.0
    agreed = len(pack_yes) >= 4 and whale_yes and (mtf_ok or mtf_yes)

    if halted:
        reason = "Motor je ugašen."
    elif frozen or triggered:
        reason = "BTC Guard drži zamrzavanje."
    elif doctrine.stand_down:
        reason = "Učitelj: stojim, uzorak nema ruba."
    elif missing:
        reason = "Nedovoljno svijeća."
    elif imbalance is None:
        reason = "Nema knjige naloga."
    elif imbalance <= doctrine.whale_block:
        reason = "Whale: ask zid, ulaz odbačen."
    elif spread is not None and spread > doctrine.max_spread:
        reason = f"Spread {_pct(spread, 2)} jede naknadu."
    elif veto:
        reason = "Skeptik ima veto."
    elif stake <= 0:
        reason = "Kelly ne da ulog."
    elif not snapshot.ready and snapshot.hub_status != "TEST":
        reason = "Tok podataka još nije spreman."
    elif agreed:
        allow = True
        names = ", ".join(pack_yes)
        reason = f"Jato {len(pack_yes)}/6 ({names}). Brzi ulaz, mozgovi se slažu."
        score = sum(item[1] for item in mind_pack.values()) + stake
    elif not mtf_ok and not mtf_yes:
        reason = "Blitz čeka 15m iznad EMA21 i 1m okret." if fast else "MTF nije 3/3."
    elif not whale_yes:
        reason = f"Whale mozak čeka jači zid od {_pct(doctrine.whale_min, 0)}."
    else:
        reason = f"Mozgovi {len(pack_yes)}/6. Čekam jače slaganje."

    return Decision(
        symbol=symbol,
        allow=allow,
        reason=reason,
        stake_fraction=stake if allow else 0.0,
        score=score,
        setup=setup,
        views=views,
        metrics=metrics,
    )
