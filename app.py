"""DOXA kokpit. Papirnati izazov, žive cijene, nijedan nalog ne ide na burzu."""

from __future__ import annotations

import html
from datetime import timedelta

import streamlit as st

from doxa.agents import evaluate
from doxa.brains import restore_brains
from doxa.config import GUARD_SYMBOL, TRADABLE
from doxa.runtime import ensure_started
from doxa.store import peek_wallet
from doxa.engine import Engine
from ui.chart import build_figure
from ui.office import journal_html, office_html, positions_html, rail_html
from ui.styles import apply_brutal_styles
from ui.text import clock, countdown, eur, pct, px

st.set_page_config(
    page_title="DOXA Quant Core",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_brutal_styles()


def _position_rows(raw_rows: list[dict]) -> list[dict]:
    rows = []
    for row in raw_rows:
        live = float(row.get("live_pct") or 0)
        rows.append(
            {
                **row,
                "entry_txt": px(float(row["entry"])),
                "sl_txt": px(float(row["sl"])),
                "tp_txt": px(float(row["tp"])),
                "live_txt": pct(live),
            }
        )
    return rows


def _state_from_disk(snapshot) -> dict | None:
    wallet = peek_wallet()
    if wallet is None:
        return None
    ghost = Engine(wallet)
    return ghost.snapshot_state(snapshot)


@st.fragment(run_every=timedelta(seconds=2))
def cockpit() -> None:
    handle = ensure_started()
    engine = handle.engine
    snapshot = handle.hub.snapshot()
    if engine is not None:
        state = engine.snapshot_state(snapshot)
        role = "MOTOR"
    else:
        state = _state_from_disk(snapshot)
        role = "GLEDATELJ"
        if state is None:
            st.info("Čekam da motor upiše dnevnik.")
            return

    doctrine = state["doctrine"]
    stats = state["stats"]
    focus_options = list(TRADABLE) + [GUARD_SYMBOL]
    focus = st.session_state.get("focus", "SOLUSDT")
    if focus not in focus_options:
        focus = "SOLUSDT"

    note = ""
    if engine is not None:
        note = engine.trail_note_for(focus)
    elif state["positions"]:
        match = next((row for row in state["positions"] if row["symbol"] == focus), None)
        note = match["note"] if match else ""

    decision = evaluate(
        snapshot,
        focus,
        doctrine,
        stats,
        frozen=state["frozen"],
        freeze_detail=state["freeze_detail"],
        halted=state["halted"],
        position_note=note,
        brains=restore_brains(state.get("brains")),
    )
    win_rate = pct(stats.win_rate) if stats.n else "prior"
    lesson = state["lessons"][-1] if state["lessons"] else "Učitelj čeka prvi trejd."
    teacher_state = "block" if state["stand_down"] else "teach"
    status = handle.hub.status
    halt_reason = str(state["halt_reason"] or "").lower()
    won = "izvršen" in halt_reason
    shut = won or "zatvoren" in halt_reason
    if won:
        status = "NALOG"
    elif shut:
        status = "ZATVOREN"
    elif state["halted"]:
        status = "STOP"
    elif state["frozen"]:
        status = "FREEZE"
    equity = float(state["equity"])
    progress = max(0.0, min(1.0, equity / float(state["target"])))
    left_col, right_col = st.columns([1.12, 0.88], gap="medium")
    with left_col:
        st.markdown(
            office_html(
                decision.views,
                countdown=countdown(state["remaining_s"]),
                equity=eur(equity),
                lesson=lesson,
                teacher_state=teacher_state,
                win_rate=win_rate,
                status=f"{role} · {status}",
                shut=shut,
                won=won,
            ),
            unsafe_allow_html=True,
        )
    with right_col:
        metric_cols = st.columns(2)
        metric_cols[0].metric("Kapital", eur(equity), delta=round(float(state["pnl"]), 2))
        metric_cols[1].metric("Rok", countdown(state["remaining_s"]))
        metric_cols = st.columns(2)
        metric_cols[0].metric("Gotovina", eur(float(state["cash"])))
        metric_cols[1].metric("Trejdovi", str(stats.n), delta=f"{stats.wins}W / {stats.losses}L")
        st.markdown(
            f"<div class='progress' title='Put do 1.000 €'><span style='width:{progress * 100:.1f}%'></span></div>",
            unsafe_allow_html=True,
        )
        st.selectbox("Par na grafu", focus_options, key="focus")
        candles = snapshot.candles.get(focus, {}).get("15m", ())
        forming = snapshot.forming.get(focus, {}).get("15m")
        position = next((row for row in state["positions"] if row["symbol"] == focus), None)
        st.plotly_chart(
            build_figure(focus, candles, forming, position),
            width="stretch",
            config={"displayModeBar": False},
        )
        st.markdown(
            f"<div class='reason'>{html.escape(decision.reason)}</div>",
            unsafe_allow_html=True,
        )
        if snapshot.hub_error:
            st.caption(snapshot.hub_error)

    st.markdown(
        rail_html(decision.views, teacher_state, lesson, win_rate),
        unsafe_allow_html=True,
    )
    st.markdown(positions_html(_position_rows(state["positions"])), unsafe_allow_html=True)
    log_rows = [{"clock": clock(float(item["t"])), "text": item["text"]} for item in state["log"]]
    st.markdown(journal_html(log_rows, state["lessons"]), unsafe_allow_html=True)

    halt_col, resume_col, reset_col, sample_col = st.columns(4)
    active = engine is not None
    with halt_col:
        if st.button("Zaustavi motor", disabled=not active, width="stretch"):
            engine.halt()
    with resume_col:
        if st.button("Nastavi", disabled=not active, width="stretch"):
            engine.resume()
    with reset_col:
        if st.button("Reset na 200 €", disabled=not active, width="stretch"):
            engine.reset()
    with sample_col:
        if st.button("Novi Kelly uzorak", disabled=not active, width="stretch"):
            engine.new_sample()

    if not active:
        st.caption("Ovaj proces samo gleda. Motor drži drugi proces, tipke su tamo.")


def main() -> None:
    st.markdown(
        """
        <div class="banner">
            <div>
                <h1><span>DOXA</span> QUANT CORE</h1>
                <p>NAREDBA: 200 € → 1.000 € u 60 minuta. Svaki agent vodi svoju igru: knjiga, momentum,
                nalet ili dip. Pamti je li ta igra zarađivala i gasi je kad gubi. Mrtav trejd grebe
                za četiri minute. Papir, živa cijena. Nema jamstva.</p>
            </div>
            <em>TIER 1 TICK · TIER 2 RADAR · TIER 3 UČITELJ</em>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cockpit()


if __name__ == "__main__":
    main()
