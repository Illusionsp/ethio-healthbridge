import os
from typing import Optional

import requests


def _get_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    return value.strip() if value and value.strip() else None


def send_doctor_alert(summary: dict) -> bool:
    """
    Sends a clinical alert to a Telegram chat via a bot.
    """
    patient_id = summary.get("patient_id", "Unknown")
    token = _get_env("TELEGRAM_BOT_TOKEN")
    chat_id = _get_env("TELEGRAM_DOCTOR_CHAT_ID") or _get_env("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Warning: TELEGRAM_BOT_TOKEN / TELEGRAM_DOCTOR_CHAT_ID not set. Telegram alerts disabled.")
        return False

    # Extract data from summary dictionary
    symptoms = ", ".join(summary.get("symptoms", []))
    raw_amharic = summary.get("raw_amharic", "N/A")
    urgency = summary.get("urgency", "Unknown").upper()
    ai_analysis = summary.get("ai_analysis", "N/A")
    action = summary.get("recommended_action", "N/A")

    # Format emoji based on urgency
    urgency_emoji = "🔴" if urgency == "HIGH" else "🟡" if urgency == "MEDIUM" else "🟢"

    text = (
        f"{urgency_emoji} *CLINICAL TRIAGE ALERT* {urgency_emoji}\n\n"
        f"*Patient ID:* `{patient_id}`\n"
        f"*Urgency:* {urgency}\n\n"
        f"*Symptoms (EN):* {symptoms}\n"
        f"*Raw Amharic:* {raw_amharic}\n\n"
        f"*AI Assessment:* {ai_analysis}\n"
        f"*Recommended Action:* {action}\n\n"
        "--- ጤናለአዳም (Tena LeAdam) Triage Support ---"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        resp = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True,
            },
            timeout=10,
        )
        if not resp.ok:
            print(f"Warning: Telegram sendMessage failed: {resp.status_code} {resp.text}")
            return False
        return True
    except Exception as e:
        print(f"Warning: Telegram sendMessage exception: {e}")
        return False

