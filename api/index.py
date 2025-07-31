import os
import asyncio
import logging
from flask import Flask, request
from telegram import Update

# Vercel's build process should handle the project structure,
# so we can import `bot` directly from the root.
from bot import get_application # This function will be created in the next step.

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Environment Variables ---
# It's crucial to set these in your Vercel project settings
BOT_TOKEN = os.getenv('BOT_TOKEN')
VERCEL_URL = os.getenv('VERCEL_URL')

# --- Flask App Initialization ---
app = Flask(__name__)

# We need to get the application instance from our bot logic.
# The get_application function will set up all the handlers.
application = get_application()

# --- Webhook Routes ---

@app.route('/')
def health_check():
    """A simple health check endpoint to confirm the server is running."""
    return "OK", 200

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
async def webhook():
    """
    This is the main webhook endpoint.
    Telegram will send updates to this URL.
    The URL includes the bot token as a secret to prevent unauthorized requests.
    """
    try:
        data = request.get_json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return 'ok'
    except Exception as e:
        logger.error(f"Error handling update: {e}")
        return 'error', 500

@app.route('/set_webhook', methods=['GET'])
async def set_webhook_route():
    """
    A one-time endpoint to set the bot's webhook URL to the Vercel deployment URL.
    Visit this endpoint in your browser once after deploying to Vercel.
    """
    if not VERCEL_URL:
        return "VERCEL_URL environment variable not set!", 500

    # The webhook URL must point to the webhook handler route.
    webhook_url = f"https://{VERCEL_URL}/{BOT_TOKEN}"

    try:
        await application.bot.set_webhook(url=webhook_url)
        logger.info(f"Webhook set to {webhook_url}")
        return f"Webhook successfully set to {webhook_url}", 200
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return f"Failed to set webhook: {e}", 500
