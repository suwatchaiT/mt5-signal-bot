import time
import logging
import config
import mt5_connector as mt5_conn
import signals as sig_detector
import notifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log"),
    ],
)
log = logging.getLogger(__name__)

# Track last signal per (symbol, type, direction) to avoid duplicate alerts
_last_signals: dict[tuple, float] = {}
COOLDOWN_SECONDS = 3600  # minimum gap between identical alerts


def should_send(signal: sig_detector.Signal) -> bool:
    key = (signal.symbol, signal.signal_type, signal.direction)
    last = _last_signals.get(key, 0)
    if time.time() - last >= COOLDOWN_SECONDS:
        _last_signals[key] = time.time()
        return True
    return False


def run():
    log.info("Connecting to MT5...")
    if not mt5_conn.connect():
        log.error("MT5 connection failed. Check credentials and that MT5 is running.")
        return

    log.info("MT5 connected. Monitoring: %s on %s", config.SYMBOLS, config.TIMEFRAME)
    notifier.send_text(
        f"🤖 <b>MT5 Signal Bot started</b>\n"
        f"Symbols: {', '.join(config.SYMBOLS)}\n"
        f"Timeframe: {config.TIMEFRAME}"
    )

    try:
        while True:
            for symbol in config.SYMBOLS:
                df = mt5_conn.get_rates(symbol)
                if df is None or len(df) < 50:
                    log.warning("Not enough data for %s, skipping.", symbol)
                    continue

                found = sig_detector.detect(symbol, df)
                for s in found:
                    if should_send(s):
                        log.info("Signal: %s %s %s — %s", s.symbol, s.signal_type, s.direction, s.detail)
                        ok = notifier.send(s)
                        if not ok:
                            log.warning("Telegram send failed for %s", s.symbol)

            time.sleep(config.POLL_INTERVAL)

    except KeyboardInterrupt:
        log.info("Bot stopped by user.")
        notifier.send_text("🛑 MT5 Signal Bot stopped.")
    finally:
        mt5_conn.disconnect()


if __name__ == "__main__":
    run()
