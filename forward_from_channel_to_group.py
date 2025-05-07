import os
import re
import time
import requests
import asyncio
from telethon import TelegramClient, events

# ==== Cấu hình ====
api_id = 27880664
api_hash = 'aee3ae5d6b0e8f6740b238e4e6a40885'

source_channels = [-1001526301244, -1001170425779]  # Danh sách kênh gốc
my_forward_channel = -1002382868937  # 🔁 Kênh riêng của bạn

save_path = "ForwardImages"
os.makedirs(save_path, exist_ok=True)

# ==== Khởi tạo client ====
client = TelegramClient('ocr_combined_bot', api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    if event.photo:
        # 📥 Tải ảnh về thư mục
        file_path = await event.download_media(file=save_path)
        print(f"✅ Đã tải ảnh từ kênh nguồn {event.chat_id} → {file_path}")

        # 📤 Forward ảnh sang kênh riêng
        await client.send_file(my_forward_channel, file_path)
        print(f"📤 Đã forward ảnh sang kênh: {my_forward_channel}")

        # 🗑️ Xoá file ảnh sau khi đã forward
        try:
            os.remove(file_path)
            print(f"🧹 Đã xoá ảnh tạm: {file_path}")
        except Exception as e:
            print(f"❌ Không thể xoá ảnh {file_path}: {e}")

if __name__ == '__main__':
    print("🚀 Bot forward ảnh đã khởi động...")
    client.start()
    client.run_until_disconnected()
