import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# -------------------------
# Environment & Bot Setup
# -------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not set in environment variables!")

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# -------------------------
# Async Command Handlers
# -------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! This is your bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📝 Available commands:\n/start\n/help")

# -------------------------
# Telegram Application
# -------------------------
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

# -------------------------
# Webhook Route
# -------------------------
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    """Receive updates from Telegram and process them asynchronously"""
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    asyncio.run(application.process_update(update))
    return "ok", 200

# -------------------------
# Transaction Notification
# -------------------------
@app.route("/notify_transaction", methods=["POST"])
def notify_transaction():
    """Send transaction updates to users asynchronously"""
    data = request.json
    try:
        user_id = data["user_id"]
        amount = data.get("amount", 0)
        status = data.get("status", "Unknown")
        asyncio.run(bot.send_message(user_id, f"💰 Transaction: ₹{amount}\nStatus: {status}"))
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------------
# Keep Alive (Render)
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
