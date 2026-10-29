"""15-minutni graf s crvenim stopom i zelenim ciljem."""

from __future__ import annotations

from datetime import datetime

import plotly.graph_objects as go

from doxa.types import Candle
from ui.text import WARSAW, px


def _stamp(open_time: int) -> datetime:
    return datetime.fromtimestamp(open_time / 1000, WARSAW)


def build_figure(symbol: str, candles: tuple[Candle, ...] | list[Candle], forming: Candle | None, position: dict | None):
    rows = list(candles[-90:])
    if forming is not None and (not rows or forming.open_time != rows[-1].open_time):
        rows.append(forming)
    figure = go.Figure()
    if rows:
        figure.add_trace(
            go.Candlestick(
                x=[_stamp(candle.open_time) for candle in rows],
                open=[candle.open for candle in rows],
                high=[candle.high for candle in rows],
                low=[candle.low for candle in rows],
                close=[candle.close for candle in rows],
                name=symbol,
                increasing_line_color="#3dff8a",
                decreasing_line_color="#ff3358",
                increasing_fillcolor="#143528",
                decreasing_fillcolor="#3a1420",
                whiskerwidth=0.4,
            )
        )
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#0b121b",
        height=430,
        margin=dict(l=8, r=8, t=42, b=8),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        title=dict(text=f"{symbol} · 15m · živa cijena", font=dict(size=14, color="#d7fff4"), x=0.01),
        xaxis=dict(gridcolor="rgba(120,160,170,.12)", tickfont=dict(color="#8eacb4")),
        yaxis=dict(gridcolor="rgba(120,160,170,.12)", tickfont=dict(color="#8eacb4"), side="right"),
    )
    if not rows:
        figure.add_annotation(text="Čekam 15m svijeće s Binancea", showarrow=False, font=dict(color="#8eacb4"))
        return figure
    if position:
        entry = float(position["entry"])
        stop = float(position["sl"])
        target = float(position["tp"])
        stop_label = "SL trail" if stop >= entry * 0.999 else "SL"
        figure.add_hline(
            y=target,
            line_color="#3dff8a",
            line_width=1.6,
            annotation_text=f"TP {px(target)}",
            annotation_font_color="#3dff8a",
            annotation_position="right",
        )
        figure.add_hline(
            y=stop,
            line_color="#ff3358",
            line_width=1.6,
            annotation_text=stop_label,
            annotation_font_color="#ff3358",
            annotation_position="right",
        )
        figure.add_hline(
            y=entry,
            line_color="#8fb9c9",
            line_dash="dot",
            line_width=1,
            annotation_text="ULAZ",
            annotation_font_color="#8fb9c9",
            annotation_position="left",
        )
    return figure
