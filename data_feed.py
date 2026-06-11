from __future__ import annotations

import logging
import pandas as pd
import yfinance as yf
import config

log = logging.getLogger(__name__)

# Map MT5-style symbols to Yahoo Finance tickers
_SYMBOL_MAP = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X",
    "AUDUSD": "AUDUSD=X",
    "USDCAD": "USDCAD=X",
    "USDCHF": "USDCHF=X",
    "NZDUSD": "NZDUSD=X",
    "XAUUSD": "GC=F",   # gold futures
    "XAGUSD": "SI=F",   # silver futures
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
}

# Map MT5-style timeframes to yfinance (interval, period) pairs.
# Period is sized to return ~200 bars for the indicators.
_TIMEFRAME_MAP = {
    "M5": ("5m", "5d"),
    "M15": ("15m", "10d"),
    "M30": ("30m", "20d"),
    "H1": ("1h", "40d"),
    "H4": ("4h", "150d"),
    "D1": ("1d", "1y"),
}


def yahoo_ticker(symbol: str) -> str:
    return _SYMBOL_MAP.get(symbol.upper(), symbol)


def get_rates(symbol: str, count: int = 200, timeframe: str | None = None) -> pd.DataFrame | None:
    interval, period = _TIMEFRAME_MAP.get(timeframe or config.TIMEFRAME, ("1h", "40d"))
    try:
        df = yf.download(
            yahoo_ticker(symbol),
            interval=interval,
            period=period,
            progress=False,
            auto_adjust=True,
        )
    except Exception as e:
        log.warning("Data fetch failed for %s: %s", symbol, e)
        return None

    if df is None or df.empty:
        return None

    # yfinance may return MultiIndex columns when fetching a single ticker
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.reset_index().rename(columns=str.lower)
    df = df.rename(columns={"datetime": "time", "date": "time"})
    df = df.dropna(subset=["close"])
    return df.tail(count).reset_index(drop=True)
