# makanApa (Serverless Edition)

makanApa is a Telegram bot that facilitates food and item delivery within the International Islamic University Malaysia (IIUM). It connects customers with runners (delivery personnel) to fulfill orders. This version has been refactored to run on a serverless platform like Vercel.

## Features

*   Food and item delivery via Telegram
*   Order management with a PostgreSQL backend
*   Runner notifications in a dedicated group
*   Serverless architecture for scalability and cost-efficiency

## Setup for Deployment

This project is designed for deployment on **Vercel**.

1.  **Fork this Repository:**
    Create a fork of this repository in your GitHub account.

2.  **Set up a PostgreSQL Database:**
    You need a publicly accessible PostgreSQL database. You can get one for free from services like:
    *   **Vercel Postgres** (Recommended if deploying on Vercel)
    *   **Neon**
    *   **Supabase**

    After setting up the database, you will get a **Database Connection URL**. It will look something like this: `postgres://user:password@host:port/dbname`.

3.  **Deploy to Vercel:**
    *   Go to your Vercel dashboard and create a new project.
    *   Import your forked GitHub repository.
    *   Vercel will automatically detect it's a Python project and use the settings in `vercel.json`.
    *   In the "Environment Variables" section, add the following:
        *   `BOT_TOKEN`: The API token for your Telegram bot from BotFather.
        *   `RUNNER_GROUP_ID`: The chat ID of the Telegram group for runners.
        *   `DATABASE_URL`: The connection URL for your PostgreSQL database from Step 2.

4.  **Initialize the Database:**
    After the first deployment, you need to run the database setup script. You can do this by temporarily adding a one-off script or by using a database client to run the SQL commands from `database.py`. A simpler way is to add a temporary endpoint in `api/index.py` that calls `setup_database()`, deploy, hit the endpoint once, and then remove it.

5.  **Set the Telegram Webhook:**
    *   Once your project is deployed, Vercel will give you a domain (e.g., `your-project-name.vercel.app`).
    *   Take your bot token and your Vercel domain and set the webhook by visiting the following URL in your browser (replace the bracketed parts):
        ```
        https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<your-project-name.vercel.app>/api/bot
        ```
    *   You should see a success message from Telegram. Your bot is now live!

## File Descriptions

*   `api/index.py`: The serverless function entry point. Contains the Flask web server that handles webhooks from Telegram.
*   `bot.py`: Contains the core logic and conversation handlers for the Telegram bot.
*   `database.py`: Contains functions to connect to the PostgreSQL database and set up the required tables and sequences.
*   `vercel.json`: Configuration file for Vercel deployment.
*   `requirements.txt`: The list of Python dependencies.

## Contributing

Contributions are welcome! Please submit a pull request with your changes.
