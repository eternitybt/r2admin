import sys
from telethon import TelegramClient, events, sync

# Your credentials from my.telegram.org
api_id = sys.argv[1]
api_hash = sys.argv[2]
phone = sys.argv[3]
#bot_username = '@c3po_cron_bot'
bot_username = 'c3po_cron_bot'  # The username of your first bot (e.g., 'myfirstbot')

print(f'api_id: {api_id}')
print(f'api_hash: {api_hash}')
print(f'phone: {phone}')
print(f'bot_username: {bot_username}')

# Create the client
client = TelegramClient('userbot_session', api_id, api_hash)

async def main():
    # Start the client (will prompt for login code if needed)
    await client.start(phone=phone)
    
    # Get the entity for the bot (starts a chat if not already open)
    bot_entity = await client.get_entity(bot_username)
    
    # Send a message to the bot
    await client.send_message(bot_entity, 'Hello from the userbot!')
    
    # Listen for responses from the bot
    @client.on(events.NewMessage(from_users=bot_username))
    async def handler(event):
        print(f"Received from bot: {event.message.text}")
        # Respond back if needed, e.g., await event.reply('Got it!')

    print("Userbot is running and connected to the bot.")
    await client.run_until_disconnected()

# Run the client
with client:
    client.loop.run_until_complete(main())
