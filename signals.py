from dataclasses import dataclass
import pandas as pd
import config


@dataclass
class Signal:
    symbol: str
    signal_type: str   # "MA_CROSS", "RSI", "MACD_CROSS"
    direction: str     # "BUY" or "SELL"
    detail: str        # human-readable detail


def _ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def _rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, float("nan"))
    return 100 - (100 / (1 + rs))


def detect(symbol: str, df: pd.DataFrame) -> list[Signal]:
    signals: list[Signal] = []
    close = df["close"]

    # Moving average crossover
    fast = _ema(close, config.MA_FAST)
    slow = _ema(close, config.MA_SLOW)
    # Crossover: previous bar fast was below slow, current bar fast is above slow (or vice versa)
    if fast.iloc[-2] < slow.iloc[-2] and fast.iloc[-1] > slow.iloc[-1]:
        signals.append(Signal(symbol, "MA_CROSS", "BUY",
            f"EMA{config.MA_FAST} crossed above EMA{config.MA_SLOW} "
            f"(fast={fast.iloc[-1]:.5f}, slow={slow.iloc[-1]:.5f})"))
    elif fast.iloc[-2] > slow.iloc[-2] and fast.iloc[-1] < slow.iloc[-1]:
        signals.append(Signal(symbol, "MA_CROSS", "SELL",
            f"EMA{config.MA_FAST} crossed below EMA{config.MA_SLOW} "
            f"(fast={fast.iloc[-1]:.5f}, slow={slow.iloc[-1]:.5f})"))

    # RSI
    rsi = _rsi(close, config.RSI_PERIOD)
    prev_rsi, curr_rsi = rsi.iloc[-2], rsi.iloc[-1]
    if prev_rsi >= config.RSI_OVERSOLD and curr_rsi < config.RSI_OVERSOLD:
        signals.append(Signal(symbol, "RSI", "SELL",
            f"RSI entered oversold zone: {curr_rsi:.1f}"))
    elif prev_rsi <= config.RSI_OVERSOLD and curr_rsi > config.RSI_OVERSOLD:
        signals.append(Signal(symbol, "RSI", "BUY",
            f"RSI exited oversold zone: {curr_rsi:.1f}"))
    elif prev_rsi <= config.RSI_OVERBOUGHT and curr_rsi > config.RSI_OVERBOUGHT:
        signals.append(Signal(symbol, "RSI", "SELL",
            f"RSI entered overbought zone: {curr_rsi:.1f}"))
    elif prev_rsi >= config.RSI_OVERBOUGHT and curr_rsi < config.RSI_OVERBOUGHT:
        signals.append(Signal(symbol, "RSI", "BUY",
            f"RSI exited overbought zone: {curr_rsi:.1f}"))

    # MACD signal-line crossover
    macd_line = _ema(close, config.MACD_FAST) - _ema(close, config.MACD_SLOW)
    signal_line = _ema(macd_line, config.MACD_SIGNAL)
    if macd_line.iloc[-2] < signal_line.iloc[-2] and macd_line.iloc[-1] > signal_line.iloc[-1]:
        signals.append(Signal(symbol, "MACD_CROSS", "BUY",
            f"MACD crossed above signal line "
            f"(MACD={macd_line.iloc[-1]:.5f}, Signal={signal_line.iloc[-1]:.5f})"))
    elif macd_line.iloc[-2] > signal_line.iloc[-2] and macd_line.iloc[-1] < signal_line.iloc[-1]:
        signals.append(Signal(symbol, "MACD_CROSS", "SELL",
            f"MACD crossed below signal line "
            f"(MACD={macd_line.iloc[-1]:.5f}, Signal={signal_line.iloc[-1]:.5f})"))

    return signals
