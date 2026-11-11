import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)



def build_message(level, rain3, shelters):
    s = shelters[0] if shelters else None
    shelter_en = f"{s['name']} ({s['dist_km']} km)" if s else "N/A"
    en = (f"FLOOD ALERT (prototype)\nRisk: {level}\nForecast rain (3 days): {rain3} mm\n"
          f"Nearest shelter: {shelter_en}\nOfficial warnings: IMD / OSDMA.")
    od = (f"ବନ୍ୟା ସତର୍କତା (ପ୍ରୋଟୋଟାଇପ୍)\nବିପଦ ସ୍ତର: {level}\n"
          f"ଆଗାମୀ ୩ ଦିନର ବର୍ଷା: {rain3} mm\nନିକଟତମ ଆଶ୍ରୟସ୍ଥଳ: {shelter_en}")
    return od + "\n\n" + en

def send_telegram(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError(".env mein TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID nahi mila")
    r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      data={"chat_id": chat_id, "text": text}, timeout=15)
    if not r.ok:
        raise RuntimeError(f"Telegram error {r.status_code}: {r.json().get('description')}")
    return r.json()