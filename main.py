from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from flask import Flask, request, jsonify
import asyncio
import threading
import os

# =====================
# Telegram Bot Token
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Set your bot token in Render environment variables
BOT_USERNAME = os.getenv("BOT_USERNAME")  # Your bot username without @, e.g., "XeoWalletBot"

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# =====================
# Telegram Commands
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = (
        f"👋 Hello {user.first_name}!\n\n"
        "Welcome to XeoWallet Bot.\n"
        "You will receive notifications for all your wallet transactions here.\n\n"
        "Use /help to see available commands."
    )
    await update.message.reply_text(msg)

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📝 *Available Commands & Contacts:*\n\n"
        "/start - Start the bot\n"
        "/help - Show this message\n\n"
        "*Channel:* XeoWallet\n"
        "*Developer:* @GAMENTER\n\n"
        "All wallet transactions will be notified automatically."
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

# =====================
# Transaction Notification Function
# =====================
def send_transaction_notification(data: dict):
    user_id = data.get("user_id")
    t_type = data.get("type")
    amount = data.get("amount")
    status = data.get("status")
    sender = data.get("sender", "N/A")
    comment = data.get("comment", "No comment")
    balance = data.get("balance")

    if not user_id:
        return

    # Message formatting
    msg = (
        f"💰 *Transaction Alert!*\n\n"
        f"*Type:* {t_type}\n"
        f"*Amount:* ₹{amount}\n"
        f"*Status:* {status}\n"
        f"*Sender:* {sender}\n"
        f"*Comment:* {comment}\n"
        f"*New Balance:* ₹{balance}"
    )

    # Inline button to open bot mini app
    bot_url = f"tg://resolve?domain={BOT_USERNAME}&start=mini"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("💼 View Wallet", url=bot_url)]]
    )

    # Send the message
    asyncio.run(bot.send_message(chat_id=user_id, text=msg, parse_mode="Markdown", reply_markup=keyboard))

# =====================
# Flask Route for Lovable Website
# =====================
@app.route("/notify_transaction", methods=["POST"])
def notify_transaction():
    data = request.json
    try:
        threading.Thread(target=send_transaction_notification, args=(data,)).start()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================
# Run Telegram Bot with Flask
# =====================
def run_telegram_bot():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.run_polling()

# =====================
# Start Flask and Bot
# =====================
if __name__ == "__main__":
    # Start bot in a separate thread
    threading.Thread(target=run_telegram_bot).start()

    # Run Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
