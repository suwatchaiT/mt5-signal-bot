# Signal Bot

Monitors forex / gold / crypto prices for technical indicator signals and sends Telegram alerts. Cross-platform (macOS, Linux, Windows) — uses Yahoo Finance data, no MT5 terminal or broker account needed.

**Signals detected**
- EMA crossover (fast/slow configurable)
- RSI overbought / oversold zones
- MACD signal-line crossover

## Setup

Requires Python 3.9+.

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env with your Telegram credentials
python main.py
```

## Configuration

All settings live in `.env` — see `.env.example` for every option.

| Variable | Default | Description |
|---|---|---|
| `TELEGRAM_TOKEN` | — | BotFather token |
| `TELEGRAM_CHAT_ID` | — | Your chat or channel ID |
| `SYMBOLS` | `EURUSD,GBPUSD,XAUUSD` | Comma-separated symbols |
| `TIMEFRAME` | `H1` | M5 M15 M30 H1 H4 D1 |
| `MA_FAST` / `MA_SLOW` | `9` / `21` | EMA periods |
| `RSI_PERIOD` | `14` | RSI lookback |
| `RSI_OVERBOUGHT` / `RSI_OVERSOLD` | `70` / `30` | RSI thresholds |
| `MACD_FAST` / `MACD_SLOW` / `MACD_SIGNAL` | `12` / `26` / `9` | MACD periods |
| `POLL_INTERVAL` | `60` | Seconds between checks |

Supported symbols: EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, USDCHF, NZDUSD, XAUUSD (gold), XAGUSD (silver), BTCUSD, ETHUSD. Other Yahoo Finance tickers can be used directly (e.g. `AAPL`, `^GSPC`).

## Telegram setup

1. Message [@BotFather](https://t.me/BotFather) → `/newbot`
2. Copy the token to `TELEGRAM_TOKEN`
3. Message your bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your `chat_id`

## Notes

- Yahoo Finance intraday data is slightly delayed (~1–15 min depending on market); fine for indicator alerts, not for HFT.
- Identical alerts are rate-limited to once per hour.
- Logs are written to `bot.log`.
