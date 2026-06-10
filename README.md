# MT5 Signal Bot

Monitors MetaTrader 5 for technical indicator signals and sends Telegram alerts.

**Signals detected**
- EMA crossover (fast/slow configurable)
- RSI overbought / oversold zones
- MACD signal-line crossover

## Requirements

- Windows with MetaTrader 5 installed and running
- Python 3.11+

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env with your credentials
python main.py
```

## Configuration

All settings live in `.env` — see `.env.example` for every option.

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_TOKEN` | — | BotFather token |
| `TELEGRAM_CHAT_ID` | — | Your chat or channel ID |
| `SYMBOLS` | `EURUSD,GBPUSD,XAUUSD` | Comma-separated symbols |
| `TIMEFRAME` | `H1` | M1 M5 M15 M30 H1 H4 D1 |
| `MA_FAST` / `MA_SLOW` | `9` / `21` | EMA periods |
| `RSI_PERIOD` | `14` | RSI lookback |
| `RSI_OVERBOUGHT` / `RSI_OVERSOLD` | `70` / `30` | RSI thresholds |
| `MACD_FAST` / `MACD_SLOW` / `MACD_SIGNAL` | `12` / `26` / `9` | MACD periods |
| `POLL_INTERVAL` | `60` | Seconds between checks |

## Telegram setup

1. Message [@BotFather](https://t.me/BotFather) → `/newbot`
2. Copy the token to `TELEGRAM_TOKEN`
3. Message your bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your `chat_id`
