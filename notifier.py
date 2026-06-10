import requests
import config
from signals import Signal

_DIRECTION_EMOJI = {"BUY": "🟢", "SELL": "🔴"}
_TYPE_LABEL = {
    "MA_CROSS": "MA Crossover",
    "RSI": "RSI Alert",
    "MACD_CROSS": "MACD Crossover",
}


def _format(signal: Signal) -> str:
    emoji = _DIRECTION_EMOJI.get(signal.direction, "⚪")
    label = _TYPE_LABEL.get(signal.signal_type, signal.signal_type)
    return (
        f"{emoji} <b>{signal.symbol}</b> — {label}\n"
        f"Direction: <b>{signal.direction}</b>\n"
        f"{signal.detail}"
    )


def send(signal: Signal) -> bool:
    if not config.TELEGRAM_TOKEN or not config.TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": _format(signal),
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except requests.RequestException:
        return False


def send_text(text: str) -> bool:
    if not config.TELEGRAM_TOKEN or not config.TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except requests.RequestException:
        return False
