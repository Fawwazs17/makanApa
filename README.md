# makanApa

makanApa is a Telegram bot that facilitates food and item delivery within the International Islamic University Malaysia (IIUM). It connects customers with runners (delivery personnel) to fulfill orders.

## Features

*   Food and item delivery
*   Order management
*   Runner notifications

## Setup

1.  **Dependencies:**
    Install the required Python libraries:

    ```bash
    pip install python-telegram-bot
    ```

2.  **Database Setup:**
    Run the `database.py` file to set up the SQLite database:

    ```bash
    python database.py
    ```

3.  **Environment Variables:**
    Set the following environment variables:

    *   `BOT_TOKEN`: The API token for your Telegram bot. You can obtain this from BotFather on Telegram.
    *   `RUNNER_GROUP_ID`: The chat ID of the Telegram group where runners receive order notifications.

## Usage

1.  Run the bot:

    ```bash
    python bot.py
    ```

2.  Start the bot by sending the `/start` command to your bot on Telegram.
3.  Follow the prompts to place an order.

## File Descriptions

*   `bot.py`: Contains the main logic for the Telegram bot.
*   `database.py`: Contains the code to set up the SQLite database.
*   `data/makanApa.db`: The SQLite database file.
*   `data/order_counter.json`: A JSON file that keeps track of the next order number.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.
