import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = "https://api.freefire-api.com/v1/ff-account-info"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 FF Stats Bot is online 24/7!\n\n"
        "Send: /ff UID\n"
        "Example: /ff 811094988"
    )

async def ff_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /ff UID\nExample: /ff 811094988")
        return

    uid = context.args[0]
    await update.message.reply_text(f"⏳ Fetching stats for UID: {uid}...")

    try:
        response = requests.get(f"{API_URL}?uid={uid}", timeout=15)
        data = response.json()

        if response.status_code == 200 and data.get('basic'):
            basic = data['basic']
            nickname = basic.get('nickname', 'N/A')
            level = basic.get('level', 'N/A')
            br_rank = basic.get('rank', 'N/A')

            msg = f"**FF Stats for UID {uid}**\n\n"
            msg += f"**Nickname:** `{nickname}`\n"
            msg += f"**Level:** `{level}`\n"
            msg += f"**BR Rank:** `{br_rank}`"

            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ No data found for UID: {uid}")

    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ API error. Try again later.")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ff", ff_stats))
    logger.info("Bot running 24/7 on Render...")
    app.run_polling()

if __name__ == "__main__":
    main()
