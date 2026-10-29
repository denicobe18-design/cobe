"""Izometrijski stakleni ured i čitljiva traka agenata."""

from __future__ import annotations

import html

from doxa.types import AgentView

_ROOM_ORDER = ("mtf", "guard", "radar", "whale", "brain", "trail", "kelly", "skeptic", "terminal")


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _agent_cell(view: AgentView) -> str:
    return (
        f"<div class='cell { _esc(view.state)}'>"
        f"<div class='upright'>"
        f"<i class='op'></i><i class='mon'></i>"
        f"<span>{_esc(view.kicker)}</span>"
        f"<strong>{_esc(view.title)}</strong>"
        f"<b>{_esc(view.value)}</b>"
        f"</div></div>"
    )


def office_html(
    views: tuple[AgentView, ...] | list[AgentView],
    *,
    countdown: str,
    equity: str,
    lesson: str,
    teacher_state: str,
    win_rate: str,
    status: str,
) -> str:
    by_id = {view.id: view for view in views}
    cells: list[str] = []
    for key in _ROOM_ORDER:
        if key == "brain":
            cells.append(
                "<div class='cell brain teach'>"
                "<div class='upright'>"
                "<div class='cylinder'><b>1</b><span>BRAIN</span></div>"
                f"<em>{_esc(win_rate)}</em>"
                "</div></div>"
            )
        elif key == "terminal":
            cells.append(
                "<div class='cell armed'>"
                "<div class='upright'>"
                "<span>CASH</span><strong>KOKPIT</strong>"
                f"<b>{_esc(equity)}</b>"
                "</div></div>"
            )
        else:
            view = by_id.get(key)
            if view is None:
                continue
            cells.append(_agent_cell(view))
    return (
        "<section class='scene'>"
        "<div class='hud'>"
        "<div><span>DOXA</span> QUANT CORE</div>"
        f"<div class='rok'>⏱ ROK { _esc(countdown)}</div>"
        f"<div class='status'>{_esc(status)}</div>"
        "</div>"
        "<div class='iso'>" + "".join(cells) + "</div>"
        f"<p class='lesson'>{_esc(lesson)}</p>"
        "</section>"
    )


def rail_html(views, teacher_state: str, lesson: str, win_rate: str) -> str:
    cards = []
    for view in views:
        cards.append(
            f"<article class='agent {_esc(view.state)}'>"
            f"<header><span>{_esc(view.kicker)}</span><strong>{_esc(view.title)}</strong>"
            f"<b>{_esc(view.value)}</b></header>"
            f"<p>{_esc(view.detail)}</p></article>"
        )
    cards.append(
        f"<article class='agent {_esc(teacher_state)} brain-card'>"
        f"<header><span>T3</span><strong>UČITELJ</strong><b>{_esc(win_rate)}</b></header>"
        f"<p>{_esc(lesson)}</p></article>"
    )
    return "<div class='rail'>" + "".join(cards) + "</div>"


def positions_html(rows: list[dict]) -> str:
    if not rows:
        return "<div class='empty'>Nema otvorene pozicije. Agenti skeniraju knjigu i čekaju 3/3.</div>"
    body = []
    for row in rows:
        live = float(row.get("live_pct") or 0)
        tone = "up" if live >= 0 else "down"
        body.append(
            "<div class='pos'>"
            f"<strong>{_esc(row['symbol'])}</strong>"
            f"<span>ulaz {_esc(row['entry_txt'])}</span>"
            f"<span class='sl'>SL {_esc(row['sl_txt'])}</span>"
            f"<span class='tp'>TP {_esc(row['tp_txt'])}</span>"
            f"<span class='{tone}'>{_esc(row['live_txt'])}</span>"
            f"<em>{_esc(row['note'])}</em>"
            "</div>"
        )
    return "<div class='positions'>" + "".join(body) + "</div>"


def journal_html(entries: list[dict], lessons: list[str]) -> str:
    log_lines = "".join(
        f"<li><time>{_esc(item['clock'])}</time>{_esc(item['text'])}</li>" for item in reversed(entries)
    )
    lesson_lines = "".join(f"<li>{_esc(item)}</li>" for item in reversed(lessons))
    if not log_lines:
        log_lines = "<li class='muted'>Dnevnik je prazan. Prvi ulaz još nije došao.</li>"
    if not lesson_lines:
        lesson_lines = "<li class='muted'>Učitelj čeka prvi zatvoreni trejd.</li>"
    return (
        "<div class='journal'>"
        "<section><h3>Dnevnik</h3><ul>" + log_lines + "</ul></section>"
        "<section><h3>Učitelj</h3><ul>" + lesson_lines + "</ul></section>"
        "</div>"
    )
