import sys
import subprocess
from telethon import TelegramClient, events, sync
from pathlib import Path

CWD = Path('/Users/joel/.r2bot')
TIMEOUT_SEC = 600
API_ID = sys.argv[1]
API_HASH = sys.argv[2]
PHONE = sys.argv[3]
BOT_USERNAME = 'c3po_cron_bot'

print(f'API_ID: {API_ID}')
print(f'API_HASH: {API_HASH}')
print(f'PHONE: {PHONE}')
print(f'BOT_USERNAME: {BOT_USERNAME}')

# Create client.
client = TelegramClient('userbot_session', API_ID, API_HASH)

def command(cmd):
    global TIMEOUT_SEC

    # Check length of command.
    len_cmd = len(cmd)
    if len_cmd < 2:
        return [f'❌ Command too short (len={len_cmd}).']

    # Determine return type.
    if not cmd[0] in ['0', '1', '2', '3', '4', '5']:
        return [f'''❌ First character must be a number indicating the return type:
0: returnvalue
1: stdout
2: stderr
3: set timeout [s]
4: write to a.txt
5: append to a.txt''']

    return_type = int(cmd[0])
    cmd = cmd[1:]

    # Set timeout.
    if return_type == 3:
        try:
            TIMEOUT_SEC = int(cmd)
            return [f'TIMEOUT_SEC: {TIMEOUT_SEC}']
        except:
            return [f'❌ Error modifying timeout. TIMEOUT_SEC: {TIMEOUT_SEC}.']

    elif return_type == 4:
        try:
            with open(CWD/'a.txt', 'w') as f:
                f.write(cmd + '\n')
            return ['✅ Success.']
        except:
            return [f'❌ Error writing to a.txt.']

    elif return_type == 5:
        try:
            with open(CWD/'a.txt', 'a') as f:
                f.write(cmd + '\n')
            return ['✅ Success.']
        except:
            return [f'❌ Error appending to a.txt.']

    else:
        # Execute command.
        try:
            # Authorize request.
            user_id = str(update.effective_user.id)
            if user_id != CHAT_ID:
                return f'Not authorized (id: "{user_id}", allowed: "{CHAT_ID}").'

            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',       # avoid UnicodeDecodeError crashes
                cwd=CWD,                # necessary when launced via launchctl
                timeout=TIMEOUT_SEC,
                check=False             # don't raise exception on non-zero exit
            )

            # Get return text.
            if return_type == 0:
                return_text = str(result.returncode)
            elif return_type == 1:
                return_text = result.stdout
            else:
                return_text = result.stderr

        except subprocess.TimeoutExpired:
            return f'❌ Time-out after {TIMEOUT_SEC}s'
        except Exception as e:
            return f'❌ Exception: {str(e)}'

    # Send return text. Split long text into separate messages.
    if return_text == '':
        return ['[no return text]']

    return_msgs = []
    while True:
        if len(return_text) < 4096:
            if len(return_text) > 0:
                return_msgs.append(return_text)
            return

        send_text = return_text[0:4096]
        return_text = return_text[4096:]
        return_msgs.append(send_text)


async def main():
    # Start the client (will prompt for login code if needed)
    await client.start(phone=PHONE)
    
    # Get the entity for the bot (starts a chat if not already open)
    bot_entity = await client.get_entity(BOT_USERNAME)
    
    # Send a message to the bot
    await client.send_message(bot_entity, 'Hello from the userbot!')
    
    # Listen for responses from the bot
    @client.on(events.NewMessage(from_users=BOT_USERNAME))
    async def handler(event):
        cmd = event.message.text.strip()
        print(f'Received from bot: {cmd}')
        return_msgs = handle_cmd(cmd)
        print(return_msgs)
        for msg in return_msgs:
            await event.reply(msg)


    print(f'✅ Connected with bot {BOT_USERNAME}.')
    await client.run_until_disconnected()

# Run the client
with client:
    client.loop.run_until_complete(main())
