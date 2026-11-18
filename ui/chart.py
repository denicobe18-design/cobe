"""15-minutni graf s crvenim stopom i zelenim ciljem."""

from __future__ import annotations

from datetime import datetime

import plotly.graph_objects as go

from doxa.types import Candle
from ui.text import WARSAW, px


def _stamp(open_time: int) -> datetime:
    return datetime.fromtimestamp(open_time / 1000, WARSAW)


def build_figure(
    symbol: str,
    candles: tuple[Candle, ...] | list[Candle],
    forming: Candle | None,
    position: dict | None,
    interval: str = "1m",
):
    rows = list(candles[-70:])
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
                increasing_line_color="#8dffc8",
                decreasing_line_color="#ff5d78",
                increasing_fillcolor="#1d6b45",
                decreasing_fillcolor="#7a2438",
                whiskerwidth=0.35,
            )
        )
    figure.update_layout(
        template="plotly_dark",
        paper_bgcolor="#070c12",
        plot_bgcolor="#070c12",
        height=280,
        margin=dict(l=4, r=56, t=36, b=4),
        xaxis_rangeslider_visible=False,
        showlegend=False,
        hovermode="x unified",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#d7ece8", size=11),
        title=dict(
            text=f"{symbol}  ·  {interval}  ·  živa cijena",
            font=dict(size=13, color="#e9fff8", family="Inter, Segoe UI, sans-serif"),
            x=0.01,
            y=0.97,
        ),
        xaxis=dict(gridcolor="rgba(120,160,170,.12)", tickfont=dict(color="#7f9aa3", size=10)),
        yaxis=dict(gridcolor="rgba(120,160,170,.12)", tickfont=dict(color="#9fd8cf", size=10), side="right"),
        hoverlabel=dict(bgcolor="#101820", bordercolor="#3ee0c5", font=dict(color="#f4fffb", size=11)),
    )
    if not rows:
        figure.add_annotation(text="Čekam svijeće s Binancea", showarrow=False, font=dict(color="#8eacb4"))
        return figure
    if position is None:
        last = rows[-1].close
        figure.add_hline(
            y=last,
            line_color="rgba(215,255,244,0.45)",
            line_width=1,
            annotation_text=px(last),
            annotation_font_color="#d7fff4",
            annotation_font_size=11,
            annotation_position="right",
        )
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
