import os
import requests

token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("CHAT_ID")

url = f"https://api.telegram.org/bot{token}/sendMessage"

r = requests.post(
    url,
    data={
        "chat_id": chat_id,
        "text": "✅ Telegram connection test successful."
    },
    timeout=20
)

print("STATUS:", r.status_code)
print("RESPONSE:", r.text)

r.raise_for_status()
