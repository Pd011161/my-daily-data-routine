# run_daily.py
import requests
import json
import sqlite3
from datetime import datetime

# =========================
# 1) ยิง API ดึงข้อมูล
# =========================
response = requests.get(
    "https://copies-corner-analog-davidson.trycloudflare.com/products"
)

response.raise_for_status()

data = response.json()

# ถ้า API ไม่ได้ return list ให้แปลงเป็น list
if not isinstance(data, list):
    data = [data]

# =========================
# 2) เก็บลง SQLite
# =========================
conn = sqlite3.connect("data.db")

conn.execute("""
    CREATE TABLE IF NOT EXISTS daily_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fetched_at TEXT,
        payload TEXT
    )
""")

conn.execute(
    """
    INSERT INTO daily_data (fetched_at, payload)
    VALUES (?, ?)
    """,
    (
        datetime.now().isoformat(),
        json.dumps(data, ensure_ascii=False)
    )
)

conn.commit()
conn.close()

# =========================
# 3) สรุปข้อมูล
# =========================
detail_lines = []

# แสดงสูงสุด 10 รายการ
for idx, item in enumerate(data[:10], start=1):

    # กรณีเป็น dict
    if isinstance(item, dict):

        detail = ", ".join(
            [f"{k}: {v}" for k, v in item.items()]
        )

        detail_lines.append(f"{idx}. {detail}")

    # กรณีไม่ใช่ dict
    else:
        detail_lines.append(f"{idx}. {str(item)}")

details_text = "\n".join(detail_lines)

summary = (
    f"วันนี้ {datetime.now().strftime('%Y-%m-%d')}\n"
    f"ดึงข้อมูลได้ {len(data)} รายการ\n\n"
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
