import os
import json
import requests

# Telegram Bot Token from environment
BOT_TOKEN = os.environ.get("BOT_TOKEN")

def handler(request, response):
    if request.method != "POST":
        return response.status(405).send("Method Not Allowed")

    try:
        body = request.json()
        message = body.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text")

        if chat_id and text:
            reply = {
                "chat_id": chat_id,
                "text": f"You said: {text}"
            }
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json=reply
            )

        return response.status(200).send("OK")
    except Exception as e:
        return response.status(500).send(f"Error: {str(e)}")