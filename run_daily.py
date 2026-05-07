# run_daily.py
import requests
import json
from datetime import datetime

# =========================
# 1) ยิง API ดึงข้อมูล
# =========================
response = requests.get(
    "https://copies-corner-analog-davidson.trycloudflare.com/products"
)
response.raise_for_status()
raw = response.json()

# ดึง items จาก response
if isinstance(raw, dict) and "data" in raw:
    items = raw["data"]
elif isinstance(raw, list):
    items = raw
else:
    items = [raw]
    
# =========================
# 2) เก็บลง Supabase
# =========================
SUPABASE_URL = "https://tugabomyprbydvfovvlo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR1Z2Fib215cHJieWR2Zm92dmxvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzgxMjI2NjQsImV4cCI6MjA5MzY5ODY2NH0.g0JeR4cwDeaygmNdNMm8-eHpud689bbcgcJrEEv8fSs"

requests.post(
    f"{SUPABASE_URL}/rest/v1/daily_data",
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    },
    json={
        "fetched_at": datetime.now().isoformat(),
        "payload": items
    }
).raise_for_status()


# =========================
# 3) สรุปข้อมูล
# =========================
detail_lines = []

for idx, item in enumerate(items[:10], start=1):
    lines = [f"{idx})"]
    if isinstance(item, dict):
        for k, v in item.items():
            lines.append(f"{k}: {v}")
    else:
        lines.append(str(item))
    lines.append("--------")
    detail_lines.append("\n".join(lines))

details_text = "\n".join(detail_lines)
summary = (
    f"วันที่: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"ข้อมูล {len(items)} รายการ ดังนี้\n\n"
    f"{details_text}"
)

# =========================
# 4) ส่ง LINE
# =========================

LINE_TOKEN = "m1Fm2klMqlQWVMZh0UbzVeZSPgJnmunP2SWPyNFSgyMfR/AyWTOoK6jHuAls+DAj3NhT5fRTMFct6fIkBU+qgiZtPueS5Q7fZ4fxqvm26P1TCvPDAZTPOl4nAAK+Lb2mC5Kw/PJoTCvWQRdvZf8gxwdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "U0bf924cf13387d9709afe925ae39b1e0"

requests.post(
    "https://api.line.me/v2/bot/message/push",
    headers={
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    },
    json={
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": summary
            }
        ]
    }
)
