import requests
import os
import re
import time
from telethon import TelegramClient, sync

# === Telegram Bot để gửi kết quả về chat cá nhân ===
api_id = 27880664
api_hash = 'aee3ae5d6b0e8f6740b238e4e6a40885'
receiver_user_id = -4605282548  # 👈 ID Telegram user bạn muốn gửi kết quả về
tele_client = TelegramClient('notifier', api_id, api_hash)
tele_client.start()

# === OCR xử lý ===
def ocr_space_file(filename, api_key='helloworld', language='eng'):
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data={
                              'apikey': api_key,
                              'language': language,
                              'isOverlayRequired': False
                          })
    result = r.json()
    parsed = result.get('ParsedResults')
    if parsed and parsed[0].get('ParsedText'):
        return parsed[0]['ParsedText']
    return ""

folder = 'images'
processed = set()

def monitor_folder():
    while True:
        files = [f for f in os.listdir(folder) if f.endswith('.jpg')]
        for fname in files:
            fpath = os.path.join(folder, fname)
            if fpath in processed:
                continue
            try:
                print(f"🔍 Đang xử lý ảnh: {fname}")
                text = ocr_space_file(fpath)
                if not text.strip():
                    warn = f"⚠️ OCR không đọc được nội dung từ ảnh: {fname}"
                    print(warn)
                    tele_client.send_message(receiver_user_id, warn)
                    os.remove(fpath)
                    continue

                signal = {"type": None, "symbol": None, "entry": None, "sl": None, "tp": None}
                lines = text.upper().split('\n')
                for line in lines:
                    if "BUY" in line:
                        signal["type"] = "BUY"
                    elif "SELL" in line:
                        signal["type"] = "SELL"
                    if signal["symbol"] is None:
                        sym_match = re.findall(r"[A-Z]{3,6}", line)
                        if sym_match:
                            signal["symbol"] = sym_match[0]
                    if "SL" in line and signal["sl"] is None:
                        signal["sl"] = re.findall(r"\d+\.?\d*", line)[-1]
                    if "TP" in line and signal["tp"] is None:
                        match = re.findall(r"\d+\.?\d*", line)
                        if match:
                            signal["tp"] = match[0]
                    if signal["entry"] is None and any(char.isdigit() for char in line) and "SL" not in line and "TP" not in line:
                        match = re.findall(r"\d+\.?\d*(?:[-–]\d+\.?\d*)?", line)
                        if match:
                            signal["entry"] = match[0]

                print("📊 Tín hiệu:", signal)
                receiver_url = "http://localhost:5000/api/receive-signal"
                res = requests.get(receiver_url, params=signal)
                print(f"📡 Gửi API: {res.status_code} - {res.text}")

                # Gửi thông báo về Telegram nếu thành công
                msg = (
                    f"📤 Đã gửi tín hiệu:\n"
                    f"Loại: {signal['type']}\n"
                    f"Symbol: {signal['symbol']}\n"
                    f"Entry: {signal['entry']}\n"
                    f"SL: {signal['sl']}\n"
                    f"TP: {signal['tp']}"
                )
                tele_client.send_message(receiver_user_id, msg)

                os.remove(fpath)
                print(f"🗑️ Đã xoá ảnh: {fname}")
                processed.add(fpath)
            except Exception as e:
                err = f"❌ Lỗi xử lý ảnh {fname}: {e}"
                print(err)
                tele_client.send_message(receiver_user_id, err)
                
if __name__ == '__main__':
    monitor_folder()