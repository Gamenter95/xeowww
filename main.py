import os
import asyncio
from flask import Flask, request, jsonify
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, ContextTypes, Application

# =====================
# Environment Variables
# =====================
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = "XeoWalletBot"  # your bot username without @

app = Flask(__name__)
bot = Bot(token=BOT_TOKEN)

# =====================
# Telegram Command Handlers
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Hello {user.first_name}!\nWelcome to XeoWallet Bot.\nUse /help to see commands."
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Commands:\n/start - Start bot\n/help - Show this help\n\nDeveloper: @GAMENTER",
    )

# =====================
# Application for PTB 20+
# =====================
application = Application.builder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_cmd))

# =====================
# Telegram Webhook Route
# =====================
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    asyncio.run(application.process_update(update))
    return "ok", 200

# =====================
# Transaction Notification Endpoint
# =====================
@app.route("/notify_transaction", methods=["POST"])
def notify_transaction():
    data = request.json
    try:
        user_id = data.get("user_id")
        t_type = data.get("type", "N/A")
        amount = data.get("amount", 0)
        status = data.get("status", "Unknown")
        sender = data.get("sender", "N/A")
        comment = data.get("comment", "No comment")
        balance = data.get("balance", 0)

        if not user_id:
            return jsonify({"error": "user_id missing"}), 400

        msg = (
            f"💰 *Transaction Alert!*\n\n"
            f"*Type:* {t_type}\n"
            f"*Amount:* ₹{amount}\n"
            f"*Status:* {status}\n"
            f"*Sender:* {sender}\n"
            f"*Comment:* {comment}\n"
            f"*New Balance:* ₹{balance}"
        )

        # Inline button
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💼 View Wallet", url=f"tg://resolve?domain={BOT_USERNAME}&start=mini")]]
        )

        asyncio.run(bot.send_message(
            chat_id=user_id,
            text=msg,
            parse_mode="Markdown",
            reply_markup=keyboard
        ))

        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =====================
# Keep Render Alive
# =====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
