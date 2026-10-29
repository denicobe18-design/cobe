"""Osmi agent. Uči iz zatvorenih trejdova u istom procesu, bez čekanja na oblak."""

from __future__ import annotations

import json
import os
import threading
import urllib.request
from typing import Any

from doxa.types import Doctrine

# Koliko smije pomaknuti parametar nakon jednog trejda.
_STEP = {
    "whale_min": 0.01,
    "atr_mult": 0.1,
    "rsi_veto": 1.0,
    "kelly_fraction": 0.05,
    "kelly_cap": 0.02,
}


class Teacher:
    def __init__(self) -> None:
        self._remote: dict[str, Any] | None = None
        self._lock = threading.Lock()

    def review_close(
        self,
        doctrine: Doctrine,
        *,
        pnl: float,
        mfe: float,
        pnl_pct: float,
        context: dict[str, Any],
        stats_n: int,
        win_rate: float,
        payoff: float,
    ) -> list[str]:
        lessons: list[str] = []
        imbalance = float(context.get("imbalance") or 0.0)
        flags = list(context.get("veto_flags") or [])
        won = pnl > 0

        if not won and imbalance >= doctrine.whale_min:
            doctrine.whale_min += _STEP["whale_min"]
            lessons.append("Lažan bid zid. Prag knjige dižem za 0,01.")
        elif won and imbalance >= doctrine.whale_min:
            doctrine.whale_min -= _STEP["whale_min"] * 0.5
            lessons.append("Snajper je držao. Prag knjige blago puštam.")

        if not won and len(flags) == doctrine.skeptic_flags - 1:
            doctrine.rsi_veto -= _STEP["rsi_veto"]
            lessons.append("Skeptik je bio jednu zastavicu premek. RSI veto spuštam.")

        if mfe >= 0.03 and pnl < 0:
            doctrine.atr_mult -= _STEP["atr_mult"]
            lessons.append("Bili smo u plusu pa vratili. Chandelier stežem.")
        elif won and mfe >= 0.08 and pnl_pct < mfe * 0.45:
            doctrine.atr_mult += _STEP["atr_mult"]
            lessons.append("Izašli smo prerano iz megaskoka. ATR množitelj puštam.")

        if stats_n >= doctrine.min_trades:
            if payoff < 1.0 or win_rate < 0.38:
                doctrine.kelly_fraction = max(0.15, doctrine.kelly_fraction - _STEP["kelly_fraction"])
                doctrine.kelly_cap = max(0.08, doctrine.kelly_cap - _STEP["kelly_cap"])
                doctrine.stand_down = payoff < 0.9 and win_rate < 0.35
                if doctrine.stand_down:
                    lessons.append("Rub uzorka je negativan. Gasim nove uloge dok ne krene novi uzorak.")
                else:
                    lessons.append("Serija je slaba. Režem Kelly udio.")
            elif win_rate >= 0.5 and payoff >= 1.2:
                doctrine.stand_down = False
                doctrine.kelly_fraction += _STEP["kelly_fraction"] * 0.5
                lessons.append("Uzorak drži rub. Kelly udio dižem unutar kapice.")

        updated = doctrine.clamped()
        doctrine.__dict__.update(updated.__dict__)
        if not lessons:
            lessons.append("Trejd je u dnevniku. Doktrina ostaje, nema razloga za trzaj.")
        return lessons

    def heartbeat(
        self,
        doctrine: Doctrine,
        *,
        now_s: float,
        last_entry_at: float,
        last_relax_at: float,
        sample_n: int,
    ) -> tuple[list[str], float]:
        """Ako je dugo tiho, snajper se za korak opusti. Samo prije punog uzorka."""
        if sample_n >= doctrine.min_trades:
            return [], last_relax_at
        quiet_for = now_s - last_entry_at
        since_relax = now_s - last_relax_at
        if quiet_for < 30 * 60 or since_relax < 10 * 60:
            return [], last_relax_at
        if doctrine.whale_min <= 0.62:
            return [], now_s
        doctrine.whale_min -= 0.01
        doctrine.whale_min = doctrine.clamped().whale_min
        return ["30 min bez ulaza. Prag knjige spuštam za 0,01 da učim živo tržište."], now_s

    def queue_remote(self, doctrine: Doctrine, closed_tail: list[dict[str, Any]]) -> None:
        """Opcionalni vanjski učitelj. Ne dira izlaz iz trejda; rezultat se primijeni na sljedećem ticku."""
        url = os.getenv("TEACHER_URL", "").strip()
        if not url or len(closed_tail) < 10 or len(closed_tail) % 10 != 0:
            return
        payload = {
            "doctrine": dict(doctrine.__dict__),
            "recent": closed_tail[-10:],
        }
        token = os.getenv("TEACHER_TOKEN", "").strip()

        def _send() -> None:
            request = urllib.request.Request(
                url,
                data=json.dumps(payload).encode(),
                headers={
                    "Content-Type": "application/json",
                    **({"Authorization": f"Bearer {token}"} if token else {}),
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=1.5) as response:
                    body = json.loads(response.read().decode() or "{}")
            except Exception:
                return
            if isinstance(body, dict):
                with self._lock:
                    self._remote = body

        threading.Thread(target=_send, name="doxa-teacher-remote", daemon=True).start()

    def pull_remote(self, doctrine: Doctrine) -> list[str]:
        with self._lock:
            body = self._remote
            self._remote = None
        if not body:
            return []
        incoming = body.get("doctrine") if isinstance(body, dict) else None
        if not isinstance(incoming, dict):
            return ["Vanjski učitelj je odgovorio bez doktrine. Ignoriram."]
        allowed = {
            "whale_min",
            "atr_mult",
            "rsi_veto",
            "kelly_fraction",
            "kelly_cap",
            "mtf_rsi_low",
            "mtf_rsi_high",
            "sentiment_boost",
            "whale_boost",
        }
        for key, value in incoming.items():
            if key in allowed and isinstance(value, (int, float)):
                setattr(doctrine, key, float(value))
        doctrine.__dict__.update(doctrine.clamped().__dict__)
        note = body.get("lesson")
        if isinstance(note, str) and note.strip():
            return ["Vanjski učitelj: " + note.strip()[:180]]
        return ["Vanjski učitelj je vratio parametre unutar raspona."]
