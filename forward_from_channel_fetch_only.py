from telethon import TelegramClient, events
import os

api_id = 27880664
api_hash = 'aee3ae5d6b0e8f6740b238e4e6a40885'
source_channels = [-1001526301244, -1001170425779]  # Danh sách ID các kênh cần theo dõi
save_path = "images"
os.makedirs(save_path, exist_ok=True)

client = TelegramClient('my_account', api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    if event.photo:
        file_path = await event.download_media(file=save_path)
        print(f"✅ [Webhook] Đã tải ảnh từ {event.chat_id}: {file_path}")

if __name__ == '__main__':
    print("📡 Đang lắng nghe webhook từ Telegram các kênh...")
    client.start()
    client.run_until_disconnected()