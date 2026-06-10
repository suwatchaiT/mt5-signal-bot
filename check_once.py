"""Single-pass signal check for scheduled runners (GitHub Actions).

Unlike main.py, this checks every symbol once and exits. Alert cooldown
state is persisted to state.json so repeated runs don't duplicate alerts.
"""
import json
import logging
import time
from pathlib import Path

import bot_commands
import config
import data_feed
import notifier
import signals as sig_detector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

STATE_FILE = Path("state.json")
COOLDOWN_SECONDS = 3600


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def main():
    state = load_state()
    now = time.time()
    sent = 0

    for symbol in config.SYMBOLS:
        df = data_feed.get_rates(symbol)
        if df is None or len(df) < 50:
            log.warning("Not enough data for %s, skipping.", symbol)
            continue

        for s in sig_detector.detect(symbol, df):
            key = f"{s.symbol}|{s.signal_type}|{s.direction}"
            if now - state.get(key, 0) < COOLDOWN_SECONDS:
                log.info("Cooldown active, skipping: %s", key)
                continue
            log.info("Signal: %s — %s", key, s.detail)
            if notifier.send(s):
                state[key] = now
                sent += 1
            else:
                log.warning("Telegram send failed for %s", key)

    bot_commands.handle_commands(state)

    STATE_FILE.write_text(json.dumps(state))
    log.info("Check complete. Alerts sent: %d", sent)


if __name__ == "__main__":
    main()
