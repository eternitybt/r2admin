import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes,
)

CHAT_ID = os.getenv('TG_CHAT_ID')
TOKEN = os.getenv('TG_CRON_BOT_TOKEN')


# Print "ready" message.
async def ready(application):
    try:
        await application.bot.send_message(
            chat_id=CHAT_ID,
            text='ready'
        )
        print(f'Ready message sent (chat id: {CHAT_ID}).')

    except Exception as e:
        print('"Failed to send ready message: {e}')


# Handle command.
async def command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cmd = update.message.text.strip()

    if cmd == '!update':
        # Update repo.
        return_code = os.system('bash .update.sh')
    else:
        # General shell command.
        user_id = str(update.effective_user.id)
        if user_id != CHAT_ID:
            await update.message.reply_text(f'Not authorized (id: "{user_id}", allowed: "{CHAT_ID}").')
            return
        return_code = os.system(cmd)
    await update.message.reply_text(str(return_code))


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
