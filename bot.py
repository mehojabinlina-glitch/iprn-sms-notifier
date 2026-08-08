import os
import json
import requests
from datetime import datetime

IPRN_TOKEN = os.getenv("IPRN_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

IPRN_URL = "https://api.iprn.pro/api/stock/public/edr"
STATE_FILE = "sent_ids.json"


def load_sent():
    try:
        with open(STATE_FILE, "r") as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()


def save_sent(sent):
    with open(STATE_FILE, "w") as f:
        json.dump(list(sent), f)


def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    r = requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": text
        },
        timeout=20
    )

    r.raise_for_status()


def main():

    if not IPRN_TOKEN or not TELEGRAM_TOKEN or not CHAT_ID:
        raise RuntimeError("GitHub Secrets missing")

    today = datetime.now().strftime("%Y-%m-%d")

    headers = {
        "Authorization": f"Bearer {IPRN_TOKEN}",
        "Accept": "application/json",
    }

    params = {
        "page": 1,
        "perPage": 25,
        "day": today,
    }

    response = requests.get(
        IPRN_URL,
        headers=headers,
        params=params,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()
    sent = load_sent()

    for sms in data.get("data", []):

        created_at = str(sms.get("created_at", "-"))
        service = str(sms.get("a_number", "-"))
        destination = str(sms.get("destination", "-"))
        number = str(sms.get("b_number", ""))

        sms_id = f"{created_at}|{service}|{destination}|{number}"

        if sms_id in sent:
            continue

        # Phone number mask
        if len(number) >= 6:
            masked_number = number[:3] + "******" + number[-3:]
        else:
            masked_number = "******"

        text = (
            "📩 SMS Received 📩\n\n"
            f"⏳ Time: {created_at}\n"
            f"⚙️ Service: {service}\n"
            f"🌍 Destination: {destination}\n"
            f"📱 Number: {masked_number}\n"
            "🔐 OTP: [message]\n"
        )

        send_telegram(text)

        sent.add(sms_id)

    save_sent(sent)


if __name__ == "__main__":
    main()
