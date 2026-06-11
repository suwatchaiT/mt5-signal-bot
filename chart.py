"""Render an M15 chart (candles + EMAs + trend line) for a signal."""
from __future__ import annotations

import io
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
import data_feed
from signals import Signal, _ema

log = logging.getLogger(__name__)

CHART_TIMEFRAME = "M15"
CHART_BARS = 96  # last 24 hours of M15 candles


def _draw_candles(ax, df: pd.DataFrame):
    width = 0.6
    for i, row in df.iterrows():
        up = row["close"] >= row["open"]
        color = "#26a69a" if up else "#ef5350"
        ax.plot([i, i], [row["low"], row["high"]], color=color, linewidth=0.8)
        body_low = min(row["open"], row["close"])
        body_h = abs(row["close"] - row["open"])
        ax.bar(i, body_h if body_h > 0 else 1e-12, width, bottom=body_low,
               color=color, edgecolor=color)


def render(signal: Signal) -> bytes | None:
    df = data_feed.get_rates(signal.symbol, count=CHART_BARS + 50, timeframe=CHART_TIMEFRAME)
    if df is None or len(df) < 30:
        return None
    df = df.tail(CHART_BARS).reset_index(drop=True)
    close = df["close"]

    fig, ax = plt.subplots(figsize=(10, 5), dpi=110)
    _draw_candles(ax, df)

    x = np.arange(len(df))
    ax.plot(x, _ema(close, config.MA_FAST), label=f"EMA{config.MA_FAST}",
            color="#2962ff", linewidth=1.2)
    ax.plot(x, _ema(close, config.MA_SLOW), label=f"EMA{config.MA_SLOW}",
            color="#ff6d00", linewidth=1.2)

    # Trend line: linear regression over the charted window
    slope, intercept = np.polyfit(x, close, 1)
    ax.plot(x, slope * x + intercept, "--", color="#9e9e9e", linewidth=1.4,
            label=f"Trend ({'up' if slope > 0 else 'down'})")

    # SL/TP levels from the signal
    if signal.sl and signal.tp:
        ax.axhline(signal.tp, color="#26a69a", linewidth=1, linestyle=":", label=f"TP {signal.tp:.5f}")
        ax.axhline(signal.sl, color="#ef5350", linewidth=1, linestyle=":", label=f"SL {signal.sl:.5f}")

    # X axis labels from timestamps
    if "time" in df.columns:
        ticks = np.linspace(0, len(df) - 1, 8, dtype=int)
        labels = [pd.Timestamp(df["time"].iloc[t]).strftime("%d %H:%M") for t in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, fontsize=8)

    direction_color = "#26a69a" if signal.direction == "BUY" else "#ef5350"
    ax.set_title(f"{signal.symbol} M15 — {signal.direction} signal (strength {signal.stars}/3)",
                 color=direction_color, fontweight="bold")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    return buf.getvalue()
