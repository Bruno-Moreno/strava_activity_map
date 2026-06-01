import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import requests

from src.config import TRAINING_LOG_GAP_HOURS, TRAINING_LOG_PATH
from src.training_log.store import load_training_log

ALERT_STATE_PATH = ".alert_state.json"
TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
SANTIAGO_TZ = ZoneInfo("America/Santiago")
EVENING_NUDGE_HOUR = 19
LAST_CHANCE_HOUR = 22


def _send_telegram(text: str) -> None:
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    resp = requests.post(
        TELEGRAM_API.format(token=token),
        json={"chat_id": chat_id, "text": text},
        timeout=10,
    )
    resp.raise_for_status()


def _load_state() -> dict:
    p = Path(ALERT_STATE_PATH)
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def _save_state(state: dict) -> None:
    Path(ALERT_STATE_PATH).write_text(json.dumps(state))


def _check_inactivity_gap(df: pd.DataFrame, now_utc: datetime) -> None:
    last_ts = pd.to_datetime(df["timestamp"], utc=True).max()
    gap = now_utc - last_ts.to_pydatetime()

    if gap < timedelta(hours=TRAINING_LOG_GAP_HOURS):
        hours = gap.total_seconds() / 3600
        print(f"Last training {hours:.1f}h ago — within threshold, no alert.")
        return

    state = _load_state()
    if state.get("last_alerted_gap_start") == last_ts.isoformat():
        print("Already alerted for this gap — skipping.")
        return

    hours = int(gap.total_seconds() // 3600)
    message = (
        f"⚠️ No training in the last {hours} hours. "
        f"Last activity: {last_ts.isoformat()}."
    )
    _send_telegram(message)
    _save_state({"last_alerted_gap_start": last_ts.isoformat()})
    print(f"Alert sent: {message}")


def _check_time_of_day(df: pd.DataFrame, now_utc: datetime) -> None:
    now_local = now_utc.astimezone(SANTIAGO_TZ)
    if now_local.hour < EVENING_NUDGE_HOUR:
        return

    local_dates = (
        pd.to_datetime(df["timestamp"], utc=True).dt.tz_convert(SANTIAGO_TZ).dt.date
    )
    if (local_dates == now_local.date()).any():
        print("Activity already recorded today — no nudge.")
        return

    if now_local.hour >= LAST_CHANCE_HOUR:
        message = "⏰ Last chance to exercise today!"
    else:
        message = "💪 It's time to exercise!"
    _send_telegram(message)
    print(f"Alert sent: {message}")


def check_and_alert(log_path: str = TRAINING_LOG_PATH) -> None:
    df = load_training_log(log_path)
    if df.empty:
        print("Training log is empty — skipping alert check.")
        return

    now_utc = datetime.now(timezone.utc)
    _check_inactivity_gap(df, now_utc)
    _check_time_of_day(df, now_utc)
