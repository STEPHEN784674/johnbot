import json
import os
import asyncio
import logging
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import nest_asyncio
nest_asyncio.apply()


# === CONFIG ===
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"   # 👈 Replace with your bot token
SOURCE_CHAT_ID = -1002821810309
CONFIG_FILE = "group_id.json"
DEFAULT_INTERVAL = 600  # 10 minutes
OWNER_ID = 7848024317   # 👈 Replace with your Telegram user ID
 main

last_message = None
scheduler = AsyncIOScheduler()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")


# === Load and Save Config ===
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                data = json.load(f)
                return data.get("groups", []), data.get("interval", DEFAULT_INTERVAL)
            except Exception as e:
                print(f"❌ Failed to load config: {e}")
    return [], DEFAULT_INTERVAL


def save_config(groups, interval):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"groups": groups, "interval": interval}, f, indent=2)
    print("💾 Config saved")


# === Forward Logic ===
async def forward_to_all(app: Application):
    global last_message
    if not last_message:
        print("⚠️ No message to forward yet.")
        return
    groups, _ = load_config()
    for gid in groups:
        try:
            await app.bot.forward_message(
                chat_id=int(gid),
                from_chat_id=last_message.chat_id,
                message_id=last_message.message_id
            )
            print(f"✅ Forwarded to {gid}")
        except Exception as e:
            print(f"❌ Forward failed for {gid}: {e}")
            try:
                await app.bot.copy_message(
                    chat_id=int(gid),
                    from_chat_id=last_message.chat_id,
                    message_id=last_message.message_id
                )
                print(f"✅ Copied to {gid}")
            except Exception as ce:
                print(f"❌ Copy also failed for {gid}: {ce}")


# === Message Handler for Source Group ===
async def handle_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_message
    if update.effective_chat.id == SOURCE_CHAT_ID:
        last_message = update.message
        print("📩 New source message saved.")



# === Helper: Admin Check ===
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Allow only OWNER in private, admins/creator in groups."""
    user_id = update.effective_user.id
    chat = update.effective_chat

    if chat.type == "private":
        return user_id == OWNER_ID   # Only OWNER can use in private chat

    if chat.type in ["group", "supergroup"]:
        try:
            member = await context.bot.get_chat_member(chat.id, user_id)
            return member.status in ["administrator", "creator"]
        except Exception as e:
            print(f"❌ Error checking admin in chat {chat.id}: {e}")
            return False

    return False
 main


# === Commands ===
async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("🚫 Only admins can use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /addgroup <group_id>")
        return

    group_id = context.args[0]
    groups, interval = load_config()
    if group_id in groups:
        await update.message.reply_text("Group already added.")
        return

    groups.append(group_id)
    save_config(groups, interval)
    await update.message.reply_text(f"✅ Group {group_id} added.")


async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("🚫 Only admins can use this command.")
        return

    groups, interval = load_config()
    if not groups:
        await update.message.reply_text("No groups added yet.")
        return

    msg = f"📋 Forwarding every {interval} seconds to:\n"
    msg += "\n".join(f"➤ {gid}" for gid in groups)
    await update.message.reply_text(msg)


async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("🚫 Only admins can use this command.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /setinterval <seconds>")
        return
    try:
        interval = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid interval. Must be a number.")
        return

    groups, _ = load_config()
    save_config(groups, interval)

    try:
        scheduler.remove_job("forwarder")
    except:
        pass

    scheduler.add_job(
        forward_to_all,
        'interval',
        seconds=interval,
        args=[context.application],
        id="forwarder"
    )
    await update.message.reply_text(f"✅ Forward interval set to {interval} seconds.")


# === Catch unrecognized messages in private chat ===
async def log_all_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command. Use /addgroup, /listgroups, /setinterval.")


# === Main ===
async def main():
    print("🚀 Bot is starting...")
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("addgroup", add_group, filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("listgroups", list_groups, filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(CommandHandler("setinterval", set_interval, filters=filters.ChatType.PRIVATE | filters.ChatType.GROUPS))
    app.add_handler(MessageHandler(filters.ALL & filters.ChatType.PRIVATE, log_all_private))

    # Forward source group messages
    app.add_handler(MessageHandler(filters.ALL, handle_source))

    # Start scheduler
    groups, interval = load_config()
    scheduler.add_job(forward_to_all, 'interval', seconds=interval, args=[app], id="forwarder")
    scheduler.start()

    # Setup bot menu
    await app.bot.delete_webhook(drop_pending_updates=True)
    await app.bot.set_my_commands([
        BotCommand("addgroup", "➕ Add a group"),
        BotCommand("listgroups", "📋 List all groups"),
        BotCommand("setinterval", "⏱ Set forwarding interval"),
    ])

    print("✅ Bot is live. Ready to forward and accept commands.")
    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
