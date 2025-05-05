from telethon import TelegramClient

api_id = 27880664
api_hash = 'aee3ae5d6b0e8f6740b238e4e6a40885'
client = TelegramClient('my_account', api_id, api_hash)

async def main():
    dialogs = await client.get_dialogs()
    for dialog in dialogs:
        if dialog:
            print(f"📛 Tên nhóm: {dialog.name} → ID: {dialog.id}")

client.start()
client.loop.run_until_complete(main())