import os
import re
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

folder = 'MyImages'
api_key = 'K83332761288957'

TELEGRAM_BOT_TOKEN = '7860007397:AAHaqVQWFhtoTBn3OYeEfxGegrGo5isp4bE'
TELEGRAM_CHAT_ID = -1002665715802  # Ví dụ: nhóm private, nhớ là số âm với nhóm

# OCR
def ocr_space_file(filepath):
    with open(filepath, 'rb') as f:
        response = requests.post(
            'https://api.ocr.space/parse/image',
            files={filepath: f},
            data={
                'apikey': api_key,
                'language': 'eng',
                'isOverlayRequired': False,
                'scale': True,
                'OCREngine': 2
            }
        )
    try:
        result = response.json()
        parsed = result.get('ParsedResults')
        if parsed and isinstance(parsed, list) and parsed[0].get('ParsedText'):
            return parsed[0]['ParsedText']
    except Exception as e:
        print(f"❌ Lỗi parse JSON: {e}")
    return ""

# Parse tín hiệu
def parse_signal(text):
    signal = {"type": None, "symbol": None, "entry": None, "sl": None, "tp": []}
    lines = text.upper().splitlines()

    for line in lines:
        if "BUY" in line:
            signal["type"] = "BUY"
        elif "SELL" in line:
            signal["type"] = "SELL"

        if signal["symbol"] is None:
            sym_match = re.findall(r"\b(XAU|GOLD|[A-Z]{6})\b", line)
            if sym_match:
                signal["symbol"] = "GOLD" if "GOLD" in sym_match or "XAU" in sym_match else sym_match[0]

        if signal["entry"] is None:
            entry_match = re.findall(r"(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)", line)
            if entry_match:
                signal["entry"] = f"{entry_match[0][0]}-{entry_match[0][1]}"
            else:
                single_entry = re.findall(r"\bENTRY[:\s]*([\d\.]+)", line)
                if single_entry:
                    signal["entry"] = single_entry[0]

        if signal["sl"] is None:
            sl_match = re.findall(r"SL[:.\s]*([\d\.]+)", line)
            if sl_match:
                signal["sl"] = sl_match[0]

        tp_match = re.findall(r"TP[:.\s]*([\d\.]+)", line)
        for tp in tp_match:
            if tp not in signal["tp"]:
                signal["tp"].append(tp)

    return signal

# Xử lý ảnh
def process_image(filepath):
    print(f"\n📥 File mới: {filepath}")
    text = ocr_space_file(filepath)
    print("📄 OCR text:\n", text)

    signal = parse_signal(text)
    if not all([signal["type"], signal["symbol"], signal["entry"], signal["sl"], signal["tp"]]):
        print("⚠️ Thiếu dữ liệu cần thiết, bỏ qua.")
        os.remove(filepath)
        return

    entries = signal["entry"].split("-") if "-" in signal["entry"] else [signal["entry"]]
    for entry in entries:
        data = {
            "Type": signal["type"],
            "Symbol": signal["symbol"],
            "Entry": entry.strip(),
            "SL": signal["sl"],
            "TP": signal["tp"][0]  # hoặc dùng signal["tp"] nếu bạn muốn gửi nhiều TP
        }
        print("📊 Tín hiệu:", data)
        send_to_telegram(data)

    os.remove(filepath)
    print("🗑️ Đã xoá ảnh sau xử lý.")

# Theo dõi thư mục bằng watchdog
class ImageHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.jpg'):
            time.sleep(0.8)  # ⏱️ Delay trước khi xử lý
            process_image(event.src_path)

def send_to_telegram(signal):
    msg = (
        f"📤 Đã gửi tín hiệu:\n"
        f"Type: {signal['Type']}\n"
        f"Symbol: {signal['Symbol']}\n"
        f"Entry: {signal['Entry']}\n"
        f"SL: {signal['SL']}\n"
        f"TP: {signal['TP']}"
    )
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': msg
        }
        r = requests.post(url, data=payload)
        if r.status_code == 200:
            print("📨 Đã gửi Telegram.")
        else:
            print(f"❌ Lỗi gửi Telegram: {r.text}")
    except Exception as e:
        print(f"❌ Exception gửi Telegram: {e}")

if __name__ == '__main__':
    print(f"🚀 Đang theo dõi thư mục: {folder}")
    event_handler = ImageHandler()
    observer = Observer()
    observer.schedule(event_handler, folder, recursive=False)
    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
