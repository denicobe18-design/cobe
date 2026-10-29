"""Hrvatski brojevi i sat u zoni Europe/Warsaw."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

WARSAW = ZoneInfo("Europe/Warsaw")


def eur(value: float) -> str:
    text = f"{value:,.2f}"
    return text.replace(",", " ").replace(".", ",") + " €"


def px(value: float) -> str:
    digits = 4 if abs(value) < 20 else 2
    text = f"{value:,.{digits}f}"
    return text.replace(",", " ").replace(".", ",")


def pct(value: float) -> str:
    text = f"{value * 100:,.2f}"
    return text.replace(",", " ").replace(".", ",") + "%"


def clock(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, WARSAW).strftime("%H:%M:%S")


def countdown(seconds: float) -> str:
    total = int(max(0, seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"
