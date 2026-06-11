from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

import config


@dataclass
class Signal:
    symbol: str
    signal_type: str        # comma-joined triggers, e.g. "MA_CROSS+RSI"
    direction: str          # "BUY" or "SELL"
    detail: str             # trigger descriptions
    price: float = 0.0
    candle_time: str = ""
    stars: int = 1          # confluence score 1-3
    sl: float = 0.0
    tp: float = 0.0
    rr: float = 0.0
    context: list[str] = field(default_factory=list)  # indicator readings


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


def _atr(df: pd.DataFrame, period: int) -> float:
    high, low, close = df["high"], df["low"], df["close"]
    prev_close = close.shift(1)
    tr = pd.concat(
        [high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1
    ).max(axis=1)
    return float(tr.rolling(period).mean().iloc[-1])


def detect(symbol: str, df: pd.DataFrame) -> list[Signal]:
    close = df["close"]
    price = float(close.iloc[-1])

    fast = _ema(close, config.MA_FAST)
    slow = _ema(close, config.MA_SLOW)
    rsi = _rsi(close, config.RSI_PERIOD)
    macd_line = _ema(close, config.MACD_FAST) - _ema(close, config.MACD_SLOW)
    signal_line = _ema(macd_line, config.MACD_SIGNAL)

    prev_rsi, curr_rsi = float(rsi.iloc[-2]), float(rsi.iloc[-1])

    # --- Trigger events (crossovers / zone exits on the latest bar) ---
    triggers: list[tuple[str, str, str]] = []  # (name, direction, description)

    if fast.iloc[-2] < slow.iloc[-2] and fast.iloc[-1] > slow.iloc[-1]:
        triggers.append(("MA_CROSS", "BUY",
            f"EMA{config.MA_FAST} crossed above EMA{config.MA_SLOW}"))
    elif fast.iloc[-2] > slow.iloc[-2] and fast.iloc[-1] < slow.iloc[-1]:
        triggers.append(("MA_CROSS", "SELL",
            f"EMA{config.MA_FAST} crossed below EMA{config.MA_SLOW}"))

    if prev_rsi <= config.RSI_OVERSOLD and curr_rsi > config.RSI_OVERSOLD:
        triggers.append(("RSI", "BUY", f"RSI exited oversold zone ({curr_rsi:.1f})"))
    elif prev_rsi >= config.RSI_OVERBOUGHT and curr_rsi < config.RSI_OVERBOUGHT:
        triggers.append(("RSI", "SELL", f"RSI exited overbought zone ({curr_rsi:.1f})"))
    elif prev_rsi >= config.RSI_OVERSOLD and curr_rsi < config.RSI_OVERSOLD:
        triggers.append(("RSI", "SELL", f"RSI entered oversold zone ({curr_rsi:.1f})"))
    elif prev_rsi <= config.RSI_OVERBOUGHT and curr_rsi > config.RSI_OVERBOUGHT:
        triggers.append(("RSI", "BUY", f"RSI entered overbought zone ({curr_rsi:.1f})"))

    if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
        triggers.append(("MACD_CROSS", "BUY", "MACD crossed above signal line"))
    elif macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]:
        triggers.append(("MACD_CROSS", "SELL", "MACD crossed below signal line"))

    if not triggers:
        return []

    # --- Current state of each indicator, used for confluence + context ---
    ma_state = "BUY" if fast.iloc[-1] > slow.iloc[-1] else "SELL"
    rsi_state = "BUY" if curr_rsi < 50 else "SELL"  # room to move up/down
    macd_state = "BUY" if macd_line.iloc[-1] > signal_line.iloc[-1] else "SELL"

    context = [
        f"EMA{config.MA_FAST}/{config.MA_SLOW}: {'bullish' if ma_state == 'BUY' else 'bearish'}",
        f"RSI: {curr_rsi:.1f}",
        f"MACD: {'above' if macd_state == 'BUY' else 'below'} signal line",
    ]

    atr = _atr(df, config.ATR_PERIOD)
    candle_time = str(df["time"].iloc[-1]) if "time" in df.columns else ""

    # --- One combined signal per direction that has at least one trigger ---
    signals: list[Signal] = []
    for direction in ("BUY", "SELL"):
        fired = [t for t in triggers if t[1] == direction]
        if not fired:
            continue

        # Confluence: how many of the three indicators currently agree
        stars = sum(1 for s in (ma_state, rsi_state, macd_state) if s == direction)
        stars = max(stars, 1)

        if direction == "BUY":
            sl = price - config.ATR_SL_MULT * atr
            tp = price + config.ATR_TP_MULT * atr
        else:
            sl = price + config.ATR_SL_MULT * atr
            tp = price - config.ATR_TP_MULT * atr
        rr = config.ATR_TP_MULT / config.ATR_SL_MULT

        signals.append(Signal(
            symbol=symbol,
            signal_type="+".join(t[0] for t in fired),
            direction=direction,
            detail="; ".join(t[2] for t in fired),
            price=price,
            candle_time=candle_time,
            stars=stars,
            sl=sl,
            tp=tp,
            rr=rr,
            context=context,
        ))

    return [s for s in signals if s.stars >= config.MIN_STARS]
