from telethon import TelegramClient
import os
import asyncio

api_id = 27880664
api_hash = 'aee3ae5d6b0e8f6740b238e4e6a40885'
source_channel = -1001170425779  # Rio Traders VIP - Gold Signals

save_path = "images"
os.makedirs(save_path, exist_ok=True)

client = TelegramClient('my_account', api_id, api_hash)

async def main():
    await client.start()

    messages = await client.get_messages(source_channel, limit=20)
    for msg in messages:
        if msg.photo:
            file_path = await msg.download_media(file=save_path)
            print(f"✅ Đã tải ảnh gần nhất: {file_path}")
            break
    else:
        print("❌ Không có ảnh nào trong 20 tin nhắn gần đây.")

asyncio.run(main())
