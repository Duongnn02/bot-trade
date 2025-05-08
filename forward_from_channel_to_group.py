import os
import re
import time
import requests
from telethon import TelegramClient, events

# ==== Cấu hình thông tin Telegram ====
api_id = 27880664
api_hash = 'aee3ae5d6b0e8f6740b238e4e6a40885'

# Các kênh cần theo dõi
source_channels = [-1002681855005, -1001170425779]
# Kênh hoặc nhóm riêng để forward ảnh
my_forward_channel = -1002382868937

# Thư mục tạm lưu ảnh khi vừa tải
temp_save_path = "ForwardImages"
# Thư mục OCR sẽ xử lý ảnh ở đây
ocr_folder_path = "MyImages"

# Tạo thư mục nếu chưa có
os.makedirs(temp_save_path, exist_ok=True)
os.makedirs(ocr_folder_path, exist_ok=True)

# ==== Khởi tạo Telethon Client ====
client = TelegramClient('ocr_combined_bot', api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    if event.photo:
        # 1. Tải ảnh về thư mục tạm
        file_path = await event.download_media(file=temp_save_path)
        print(f"✅ Đã tải ảnh từ kênh {event.chat_id} → {file_path}")

        # 2. Forward ảnh sang nhóm/kênh riêng
        await client.send_file(my_forward_channel, file_path)
        print(f"📤 Đã forward ảnh sang kênh riêng: {my_forward_channel}")

        # 3. Copy ảnh sang thư mục xử lý OCR
        try:
            filename = os.path.basename(file_path)
            new_path = os.path.join(ocr_folder_path, filename)
            with open(file_path, 'rb') as src, open(new_path, 'wb') as dst:
                dst.write(src.read())
            print(f"📁 Đã chuyển ảnh sang thư mục OCR: {new_path}")
        except Exception as e:
            print(f"❌ Không thể chuyển ảnh sang MyImages: {e}")

        # 4. Xoá ảnh tạm sau khi xử lý
        try:
            os.remove(file_path)
            print(f"🧹 Đã xoá ảnh tạm: {file_path}")
        except Exception as e:
            print(f"❌ Không thể xoá ảnh tạm: {e}")

if __name__ == '__main__':
    print("🚀 Bot forward + OCR webhook đã khởi động...")
    client.start()
    client.run_until_disconnected()
