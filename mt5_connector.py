import MetaTrader5 as mt5
import pandas as pd
import config

_TIMEFRAME_MAP = {
    "M1": mt5.TIMEFRAME_M1,
    "M5": mt5.TIMEFRAME_M5,
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1,
}


def connect() -> bool:
    if not mt5.initialize():
        return False
    if config.MT5_LOGIN:
        return mt5.login(config.MT5_LOGIN, config.MT5_PASSWORD, config.MT5_SERVER)
    return True


def disconnect():
    mt5.shutdown()


def get_rates(symbol: str, count: int = 200) -> pd.DataFrame | None:
    tf = _TIMEFRAME_MAP.get(config.TIMEFRAME, mt5.TIMEFRAME_H1)
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df
