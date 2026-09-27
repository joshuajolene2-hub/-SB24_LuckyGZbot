# Password Generator Bot

A Telegram bot that generates strong, random passwords using Python's `secrets` module.

## Commands
- `/start` — Show password options
- `/help` — How to use the bot

## Deploy on Railway
1. Push this repo to GitHub.
2. Create a new Railway project → Deploy from GitHub repo.
3. Add environment variables:
   - `TELEGRAM_BOT_TOKEN` — from @BotFather
   - `WEBHOOK_SECRET` — random string (e.g. `openssl rand -hex 32`)
4. Deploy. Railway auto-detects Python and runs the Procfile.

## Local Development
```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="your_token"
python main.py
