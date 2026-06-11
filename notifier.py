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
    labels = " + ".join(_TYPE_LABEL.get(t, t) for t in signal.signal_type.split("+"))
    stars = "⭐" * signal.stars
    strength = {1: "weak", 2: "moderate", 3: "strong"}.get(signal.stars, "")

    lines = [
        f"{emoji} <b>{signal.symbol} {signal.direction}</b> — {labels}",
        f"{stars} {strength} signal",
        "",
        f"Trigger: {signal.detail}",
    ]
    if signal.price:
        price_line = f"Price: <b>{signal.price:.5f}</b>"
        if signal.candle_time:
            price_line += f" | candle {signal.candle_time}"
        lines.append(price_line)
    if signal.context:
        lines.append(" | ".join(signal.context))
    if signal.sl and signal.tp:
        lines.append("")
        lines.append(
            f"Suggested SL: {signal.sl:.5f} | TP: {signal.tp:.5f} | R:R {signal.rr:.1f}"
        )
    return "\n".join(lines)


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
        ok = r.status_code == 200
    except requests.RequestException:
        return False

    if ok:
        _send_chart(signal)
    return ok


def _send_chart(signal: Signal) -> None:
    """Follow the alert with an M15 chart image. Best-effort."""
    try:
        import chart
        png = chart.render(signal)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Chart render failed: %s", e)
        return
    if not png:
        return
    url = f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendPhoto"
    try:
        requests.post(
            url,
            data={"chat_id": config.TELEGRAM_CHAT_ID,
                  "caption": f"{signal.symbol} M15 — last 24h"},
            files={"photo": (f"{signal.symbol}_m15.png", png, "image/png")},
            timeout=30,
        )
    except requests.RequestException:
        pass


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
