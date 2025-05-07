import requests
import os
import re
import time
from telethon import TelegramClient, sync

api_id = 27880664
api_hash = 'aee3ae5d6b0e8f6740b238e4e6a40885'
receiver_user_id = -4605282548
tele_client = TelegramClient('notifier_ocr', api_id, api_hash)
tele_client.start()

def ocr_space_file(filename, api_key='K83332761288957', language='eng'):
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data={
                              'apikey': api_key,
                              'language': language,
                              'isOverlayRequired': False,
                              'scale': True,
                              'OCREngine': 2
                          })
    result = r.json()
    parsed = result.get('ParsedResults')
    if parsed and parsed[0].get('ParsedText'):
        return parsed[0]['ParsedText']
    return ""

folder = 'MyImages'
processed = set()

def is_file_ready(fpath):
    try:
        with open(fpath, 'rb'):
            return True
    except:
        return False

def monitor_folder():
    while True:
        files = [f for f in os.listdir(folder) if f.endswith('.jpg')]
        for fname in files:
            fpath = os.path.join(folder, fname)
            if fpath in processed or not is_file_ready(fpath):
                continue
            try:
                time.sleep(0.3)
                print(f"🔍 Đang xử lý ảnh: {fname}")
                text = ocr_space_file(fpath)
                print("📄 OCR text:", text)

                if not text.strip():
                    print(f"⚠️ Không đọc được nội dung, xoá ảnh: {fname}")
                    time.sleep(0.3)
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
                        sl_match = re.findall(r"\d+\.?\d*", line)
                        if sl_match:
                            signal["sl"] = sl_match[-1]
                    if "TP" in line and signal["tp"] is None:
                        tp_match = re.findall(r"\d+\.?\d*", line)
                        if tp_match:
                            signal["tp"] = tp_match[0]
                    if signal["entry"] is None:
                        entry_match = re.findall(r"\d+\.?\d*\s*[-–]\s*\d+\.?\d*", line)
                        if entry_match:
                            signal["entry"] = entry_match[0].replace(" ", "")

                entries = []
                if signal["entry"]:
                    if "-" in signal["entry"]:
                        entries = signal["entry"].split("-")
                    else:
                        entries = [signal["entry"]]

                if entries:
                    for entry in entries:
                        signal_copy = signal.copy()
                        signal_copy["entry"] = entry.strip()
                        print("📊 Tín hiệu:", signal_copy)

                        # Gửi API
                        try:
                            receiver_url = "http://localhost:5000/api/receive-signal"
                            res = requests.get(receiver_url, params=signal_copy)
                            print(f"📡 Gửi API: {res.status_code} - {res.text}")
                        except Exception as e:
                            print(f"❌ Lỗi khi gửi API: {e}")

                        # Gửi về Telegram
                        try:
                            msg = (
                                f"📤 Đã gửi tín hiệu:\n"
                                f"Loại: {signal_copy['type']}\n"
                                f"Symbol: {signal_copy['symbol']}\n"
                                f"Entry: {signal_copy['entry']}\n"
                                f"SL: {signal_copy['sl']}\n"
                                f"TP: {signal_copy['tp']}"
                            )
                            tele_client.send_message(receiver_user_id, msg)
                        except Exception as e:
                            print(f"❌ Lỗi gửi Telegram: {e}")

                    time.sleep(0.3)
                    os.remove(fpath)
                    print(f"🗑️ Đã xoá ảnh: {fname}")
                else:
                    print(f"⚠️ Không tách được entry. Xoá ảnh: {fname}")
                    os.remove(fpath)

                processed.add(fpath)

            except Exception as e:
                print(f"❌ Lỗi xử lý ảnh {fname}: {e}")
                if "WinError 32" in str(e):
                    print("⏳ File đang bị khoá, sẽ thử lại sau.")

        time.sleep(1)

if __name__ == '__main__':
    monitor_folder()
