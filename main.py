import os
from flask import Flask, request, jsonify
from telegram import Bot, Update

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)

# Simple command dispatcher
def handle_command(update: Update):
    msg = update.message.text.lower() if update.message else ""
    chat_id = update.effective_chat.id

    if msg.startswith("/start"):
        bot.send_message(chat_id, "👋 Welcome! This is your bot.")
    elif msg.startswith("/help"):
        bot.send_message(chat_id, "📝 Available commands:\n/start\n/help")
    else:
        bot.send_message(chat_id, "❌ Unknown command.")

# Webhook route
@app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    handle_command(update)
    return "ok", 200

# Notification endpoint
@app.route("/notify_transaction", methods=["POST"])
def notify_transaction():
    data = request.json
    try:
        user_id = data["user_id"]
        amount = data.get("amount", 0)
        status = data.get("status", "Unknown")
        bot.send_message(user_id, f"💰 Transaction: ₹{amount}\nStatus: {status}")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Keep alive
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
