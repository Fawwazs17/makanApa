import os
import logging
from flask import Flask, request
from telegram import Update
from bot import setup_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize the bot
bot_app = setup_bot()

@app.route('/api/bot', methods=['POST'])
async def webhook():
    logger.info("Webhook received")
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    await bot_app.process_update(update)
    return 'ok'

@app.route('/api/set_webhook', methods=['GET'])
async def set_webhook():
    # Note: This is a convenience endpoint for setting the webhook.
    # It should be called once after deployment.
    # In a production environment, you would set this manually or via a CI/CD script.
    host = request.headers.get('X-Forwarded-Host') or request.host
    webhook_url = f"https://{host}/api/bot"

    # Get the application instance from bot.py
    application = setup_bot()

    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")
    return f"Webhook set to {webhook_url}"

@app.route('/')
def index():
    return 'Hello, World! This is the bot server.'

if __name__ == "__main__":
    # This part is for local development and will not be used by Vercel
    app.run(debug=True, port=os.environ.get('PORT', 8080))
