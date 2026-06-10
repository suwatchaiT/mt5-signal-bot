import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# MT5
MT5_LOGIN = int(os.getenv("MT5_LOGIN", "0"))
MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
MT5_SERVER = os.getenv("MT5_SERVER", "")

# Symbols to monitor
SYMBOLS = os.getenv("SYMBOLS", "EURUSD,GBPUSD,XAUUSD").split(",")

# Timeframe (MT5 timeframe constant name, e.g. M15, H1, H4, D1)
TIMEFRAME = os.getenv("TIMEFRAME", "H1")

# Indicator settings
MA_FAST = int(os.getenv("MA_FAST", "9"))
MA_SLOW = int(os.getenv("MA_SLOW", "21"))
RSI_PERIOD = int(os.getenv("RSI_PERIOD", "14"))
RSI_OVERBOUGHT = float(os.getenv("RSI_OVERBOUGHT", "70"))
RSI_OVERSOLD = float(os.getenv("RSI_OVERSOLD", "30"))
MACD_FAST = int(os.getenv("MACD_FAST", "12"))
MACD_SLOW = int(os.getenv("MACD_SLOW", "26"))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", "9"))

# Poll interval in seconds
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "60"))
