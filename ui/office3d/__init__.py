"""Živi 3D ured. Iframe ostaje izvan fragmenta pa se kamera ne resetira."""

from __future__ import annotations

from pathlib import Path

import streamlit.components.v1 as components

from doxa.types import AgentView

_component = components.declare_component("doxa_office", path=str(Path(__file__).parent))
_feed = components.declare_component("doxa_feed", path=str(Path(__file__).parent / "feed"))

_NAMES = {
    "whale": "Lena Vuk",
    "guard": "Marko Ilić",
    "radar": "Nina Horvat",
    "mtf": "Petra Kovač",
    "skeptic": "Ivan Babić",
    "trail": "Sara Novak",
    "kelly": "Luka Periš",
    "teacher": "Ana Marić",
}


def _clip(text: str, limit: int = 86) -> str:
    clean = " ".join(text.split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def _job(view: AgentView) -> str:
    raw = view.detail or ""
    if view.id == "radar" and "sentiment" in raw:
        sentiment = ""
        action = ""
        blob = raw.replace("{", " ").replace("}", " ").replace('"', "")
        for part in blob.split(","):
            key, _, value = part.partition(":")
            key = key.strip()
            value = value.strip()
            if key == "sentiment":
                sentiment = value
            elif key == "action":
                action = value
        raw = " · ".join(bit for bit in (sentiment, action) if bit)
    raw = raw.split(" Mozak")[0].strip(" .")
    return _clip(raw) or view.value


def people_payload(views, teacher_state: str, lesson: str, win_rate: str) -> list[dict]:
    by_id = {view.id: view for view in views}
    rows: list[dict] = []
    for key in ("whale", "guard", "radar", "mtf", "skeptic", "trail", "kelly"):
        view = by_id.get(key)
        if view is None:
            continue
        rows.append(
            {
                "id": view.id,
                "name": _NAMES[view.id],
                "role": view.title,
                "job": _job(view),
                "state": view.state,
                "value": str(view.value),
            }
        )
    rows.append(
        {
            "id": "teacher",
            "name": _NAMES["teacher"],
            "role": "UČITELJ",
            "job": _clip(lesson) or "Čeka prvi trejd.",
            "state": "block" if teacher_state == "block" else "teach",
            "value": win_rate,
        }
    )
    return rows


def office_3d(people: list[dict], *, status: str, countdown: str, equity: str, lesson: str):
    return _component(
        people=people,
        status=status,
        countdown=countdown,
        equity=equity,
        lesson=_clip(lesson, 140),
        default=None,
        key="doxa-office",
    )


def office_feed(people: list[dict], *, status: str, countdown: str, equity: str, lesson: str):
    return _feed(
        people=people,
        status=status,
        countdown=countdown,
        equity=equity,
        lesson=_clip(lesson, 140),
        default=None,
        key="doxa-feed",
    )
