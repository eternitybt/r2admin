import sys
import subprocess
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

TOKEN = sys.argv[1]
CHAT_ID = sys.argv[2]
TIMEOUT_SEC = 600


# Print ready message.
async def ready(application):
    try:
        await application.bot.send_message(
            chat_id=CHAT_ID,
            text='ready'
        )
        print(f'Ready message sent (chat id: {CHAT_ID}).')

    except Exception as e:
        print(f'Failed to send ready message: {e}')


# Handle command.
async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global TIMEOUT_SEC
    cmd = update.message.text.strip()

    # Check length of command.
    len_cmd = len(cmd)
    if len_cmd < 2:
        await update.message.reply_text(f'❌ Command too short (len={len_cmd}).')
        return

    # Determine return type.
    if not cmd[0] in ['0', '1', '2', '3', '4']:
        await update.message.reply_text(
        f'''❌ First character must be a number indicating the return type:
0: returnvalue
1: stdout
2: stderr
3: set timeout [s]
4: append to a.txt''')
        return
    return_type = int(cmd[0])
    cmd = cmd[1:]

    # Set timeout.
    if return_type == 3:
        try:
            TIMEOUT_SEC = int(cmd)
            return_text = f'TIMEOUT_SEC: {TIMEOUT_SEC}'
        except:
            return_text = f'❌ Error modifying timeout. TIMEOUT_SEC: {TIMEOUT_SEC}.'

    elif return_type == 4:
        try:
            with open('a.txt', 'a') as f:
                f.write(cmd + '\n')
            return_text = '✅ Success.'
        except:
            return_text = f'❌ Error writing to a.txt.'

    else:
        # Execute command.
        try:
            # Authorize request.
            user_id = str(update.effective_user.id)
            if user_id != CHAT_ID:
                await update.message.reply_text(f'Not authorized (id: "{user_id}", allowed: "{CHAT_ID}").')
                return

            #result = subprocess.run(
            #        cmd.split(),
            #        capture_output=True,
            #        text=True)
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',           # avoid UnicodeDecodeError crashes
                cwd='/Users/joel/.r2bot',   # necessary when launced via launchctl
                timeout=TIMEOUT_SEC,
                check=False                 # don't raise exception on non-zero exit
            )

            # Get return text.
            if return_type == 0:
                return_text = str(result.returncode)
            elif return_type == 1:
                return_text = result.stdout
            else:
                return_text = result.stderr

        except subprocess.TimeoutExpired:
            return_text = f'❌ Time-out after {TIMEOUT_SEC}s'
        except Exception as e:
            return_text = f'❌ Exception: {str(e)}'

    # Send return text. Split long text into separate messages.
    if return_text == '':
        return_text = '[no return text]'

    while True:
        if len(return_text) < 4096:
            if len(return_text) > 0:
                await update.message.reply_text(return_text)
            return

        send_text = return_text[0:4096]
        return_text = return_text[4096:]
        await update.message.reply_text(send_text)


# Create application.
application = (
    ApplicationBuilder()
    .token(TOKEN)
    .post_init(ready)
    .read_timeout(30)
    .write_timeout(30)
    .connect_timeout(30)
    .build()
)

# Define handlers.
application.add_handler(
    MessageHandler(filters.TEXT & ~filters.COMMAND, command)
)

# Start bot.
print(f'Bot is running (token: {TOKEN}).')
application.run_polling(
    poll_interval=1.0,
    drop_pending_updates=True,          # ignore old messages
    allowed_updates=Update.ALL_TYPES
)
