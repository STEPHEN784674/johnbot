import json
import logging
import os
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler


# Required for running asyncio in notebooks or environments with existing loops
import nest_asyncio
nest_asyncio.apply()

# --- Configuration ---
BOT_TOKEN = "7572402704:AAGhjMcYslge4HhnCb3b_3tYPNS9hdH6jUg"
SOURCE_CHAT_ID = -4971311674  # replace with your actual group/channel ID
FORWARD_INTERVAL = 600  # seconds

last_message = None

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_group_ids():
    if os.path.exists("group_id.json"):
        with open("group_id.json", "r") as f:
            return json.load(f)
    return []

async def forward_last_message(app: Application):
    global last_message
    if last_message:
        for target_id in load_group_ids():
            try:
                await app.bot.forward_message(
                    chat_id=target_id,
                    from_chat_id=last_message.chat_id,
                    message_id=last_message.message_id
                )
                logging.info(f"✅ Forwarded to {target_id}")
            except Exception as e:
                logging.error(f"❌ Failed to forward to {target_id}: {e}")
    else:
        logging.warning("⚠️ No message yet to forward.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_message
    if update.effective_chat.id == SOURCE_CHAT_ID:
        last_message = update.message
        logging.info("✅ Last message updated")

async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, handle_message))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(forward_last_message, 'interval', seconds=FORWARD_INTERVAL, args=[app])
    scheduler.start()

    logging.info("🤖 Bot started. Will forward every 10 seconds.")
    await app.initialize()
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.run_polling(close_loop=False)


if __name__ == "__main__":
    asyncio.run(main())



