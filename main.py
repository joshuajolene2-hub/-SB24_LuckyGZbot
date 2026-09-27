import os
import secrets
import string
import logging
from flask import Flask, request, jsonify
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# --- Configuration ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
PORT = int(os.environ.get("PORT", 8080))
RAILWAY_DOMAIN = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Flask App ---
flask_app = Flask(__name__)

# --- Password Generator ---
def generate_password(length: int = 16, use_symbols: bool = True) -> str:
    alphabet = string.ascii_letters + string.digits
    if use_symbols:
        alphabet += "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(length))


# --- Telegram App ---
app = Application.builder().token(BOT_TOKEN).build()


# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("16 chars", callback_data="gen_16"),
            InlineKeyboardButton("32 chars", callback_data="gen_32"),
        ],
        [
            InlineKeyboardButton("16 no symbols", callback_data="gen_16_nosym"),
            InlineKeyboardButton("64 chars", callback_data="gen_64"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🔐 *Secure Password Generator*\n\n"
        "Passwords are generated securely on the server.\n\n"
        "Choose an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send /start to see password options.\n"
        "Tap a button to generate a password instantly."
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("gen_"):
        parts = data.split("_")
        length = int(parts[1])
        use_symbols = "nosym" not in data
        password = generate_password(length, use_symbols)
        await query.edit_message_text(
            f"`{password}`",
            parse_mode="Markdown",
        )


app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CallbackQueryHandler(button_handler))


# --- Flask Routes ---
@flask_app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


@flask_app.route(f"/webhook/{BOT_TOKEN}", methods=["POST"])
def webhook():
    if WEBHOOK_SECRET:
        token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if token != WEBHOOK_SECRET:
            return "Unauthorized", 403

    update = Update.de_json(request.get_json(force=True), app.bot)
    app.update_queue.put_nowait(update)
    return "ok", 200


# --- Startup: register webhook ---
async def on_startup(application: Application):
    if RAILWAY_DOMAIN:
        webhook_url = f"https://{RAILWAY_DOMAIN}/webhook/{BOT_TOKEN}"
        await application.bot.set_webhook(
            url=webhook_url,
            secret_token=WEBHOOK_SECRET or None,
        )
        logger.info(f"Webhook set to {webhook_url}")


app.post_init = on_startup


# --- Run ---
if __name__ == "__main__":
    if not RAILWAY_DOMAIN:
        logger.info("Running in polling mode (local dev)")
        app.run_polling()
    else:
        logger.info(f"Starting webhook server on port {PORT}")
        flask_app.run(host="0.0.0.0", port=PORT)
