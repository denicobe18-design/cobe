"""RSI, EMA, ATR i svijećni obrasci. Zatvorene svijeće, bez crtanja unaprijed."""

from __future__ import annotations

from collections.abc import Sequence

from doxa.types import Candle


def closes(candles: Sequence[Candle]) -> list[float]:
    return [candle.close for candle in candles]


def ema(values: Sequence[float], period: int) -> float | None:
    if period <= 0 or len(values) < period:
        return None
    seed = sum(values[:period]) / period
    k = 2.0 / (period + 1.0)
    value = seed
    for price in values[period:]:
        value = price * k + value * (1.0 - k)
    return value


def rsi(values: Sequence[float], period: int = 14) -> float | None:
    """Wilderov RSI. Vraća None dok nema dovoljno koraka."""
    if period <= 0 or len(values) < period + 1:
        return None
    gains = 0.0
    losses = 0.0
    for index in range(1, period + 1):
        delta = values[index] - values[index - 1]
        if delta >= 0:
            gains += delta
        else:
            losses -= delta
    avg_gain = gains / period
    avg_loss = losses / period
    for index in range(period + 1, len(values)):
        delta = values[index] - values[index - 1]
        gain = delta if delta > 0 else 0.0
        loss = -delta if delta < 0 else 0.0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
    if avg_loss == 0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def atr(candles: Sequence[Candle], period: int = 14) -> float | None:
    if period <= 0 or len(candles) < period + 1:
        return None
    true_ranges: list[float] = []
    for index in range(1, len(candles)):
        current = candles[index]
        previous_close = candles[index - 1].close
        true_range = max(
            current.high - current.low,
            abs(current.high - previous_close),
            abs(current.low - previous_close),
        )
        true_ranges.append(true_range)
    value = sum(true_ranges[:period]) / period
    for true_range in true_ranges[period:]:
        value = (value * (period - 1) + true_range) / period
    return value


def bullish_engulfing(candles: Sequence[Candle]) -> bool:
    if len(candles) < 2:
        return False
    previous, current = candles[-2], candles[-1]
    bearish_prev = previous.close < previous.open
    bullish_now = current.close > current.open
    engulfs = current.open <= previous.close and current.close >= previous.open
    return bearish_prev and bullish_now and engulfs


def volume_divergence(candles: Sequence[Candle]) -> bool:
    """Proboj iznad lokalnog vrha na manjem volumenu od tog vrha."""
    if len(candles) < 8:
        return False
    window = candles[-16:-1] if len(candles) > 16 else candles[:-1]
    peak = max(window, key=lambda candle: candle.high)
    recent = candles[-1]
    broke_out = recent.close >= peak.high
    return broke_out and recent.volume < peak.volume


def order_book_imbalance(bids: Sequence[tuple[float, float]], asks: Sequence[tuple[float, float]]) -> float | None:
    """Udio bid notionala u zbroju bid + ask. 0.75 znači zid kupaca."""
    bid_notional = sum(price * qty for price, qty in bids if qty > 0)
    ask_notional = sum(price * qty for price, qty in asks if qty > 0)
    total = bid_notional + ask_notional
    if total <= 0:
        return None
    return bid_notional / total


def fractional_kelly(win_rate: float, payoff: float, fraction: float, cap: float) -> float:
    """Polu-Kelly: f = fraction * (p - q/b), odsječeno na [0, cap]."""
    if payoff <= 0 or fraction <= 0 or cap <= 0:
        return 0.0
    loss_rate = 1.0 - win_rate
    full = (win_rate * payoff - loss_rate) / payoff
    sized = max(0.0, full) * fraction
    return min(cap, sized)
