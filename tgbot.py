# T G   B O T
#
# Simple Telegram bot.
import os
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    filters,
    ContextTypes,
)


async def shell_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    os.system(text)
    await update.message.reply_text(f"> {text}")


# Create application.
TOKEN = os.getenv("TG_CRON_BOT_TOKEN")
app = Application.builder().token(TOKEN).build()

# Handle shell commands.
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, shell_command))

# Start bot.
print(f"Bot is running...")
app.run_polling(
    poll_interval=0.5,
    drop_pending_updates=True,   # ignore old messages
    allowed_updates=Update.ALL_TYPES
)
