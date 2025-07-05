# makanApa – IIUM e-Hailing Telegram Bot

![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)

makanApa is an open-source Telegram bot that connects customers to campus “runners” (delivery riders) for **food** and **item** deliveries within International Islamic University Malaysia (IIUM).

The project is intentionally lightweight — a single Python script backed by SQLite — so that students can self-host the bot on inexpensive servers or clouds such as Render, Fly.io or an on-premise Raspberry Pi.

---

## Table of Contents
1. [Key Features](#key-features)
2. [Architecture Overview](#architecture-overview)
3. [Quick Start](#quick-start)
4. [Configuration](#configuration)
5. [Database Schema](#database-schema)
6. [Project Structure](#project-structure)
7. [Development](#development)
8. [Deployment Guide](#deployment-guide)
9. [Troubleshooting](#troubleshooting)
10. [Contributing](#contributing)
11. [License](#license)

---

## Key Features
• Interactive Telegram conversation flow powered by `python-telegram-bot v20`.
• Separate user roles: **customers** (place orders) & **runners** (accept orders from a private group chat).
• Persistent order, customer and runner records stored in SQLite (schema described below).
• Inline-keyboard UI with automated order summaries, confirmations and cancellation.
• Pluggable authentication: add user IDs to `data/devlist.json` or rely on dynamic registration.
• Extensive logging to `data/bot.log` for audit and debugging.

---

## Architecture Overview
A high-level view of how the pieces fit together:

```mermaid
graph LR
    subgraph Telegram
        A[Customer] -- /start & inline queries --> B(Bot)
        C[Runner Group] -- inline "Accept order" --> B
    end
    B -- SQLite (via `database.py`) --> D[(makanApa.db)]
    B -- writes --> E[data/bot.log]
```

A more detailed explanation is available in `docs/architecture.md`.

---

## Quick Start
Prerequisites: **Python 3.10+** and **git**.

```bash
# 1. Clone the repository
$ git clone https://github.com/your-username/makanApa.git && cd makanApa

# 2. Install dependencies (preferably in a venv)
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# 3. Configure the bot
$ cp .env.example .env
$ nano .env  # fill in BOT_TOKEN and RUNNER_GROUP_ID

# 4. Bootstrap the SQLite database & helper files
$ python database.py  # creates data/makanApa.db & data/order_counter.json

# 5. Run the bot 🎉
$ python bot.py
```

Open Telegram, search for your bot username and send `/start` to begin ordering.

---

## Configuration
The application reads sensitive values from environment variables stored in `.env` (loaded via `python-dotenv`).

Variable | Description | Example
---------|-------------|--------
`BOT_TOKEN` | Telegram bot token obtained from BotFather | `123456:ABCDEF`  
`RUNNER_GROUP_ID` | Chat ID of the private runners group (negative ID for supergroups) | `-1001978023456`

Copy `.env.example` and update the placeholders:

```bash
cp .env.example .env
```

---

## Database Schema
SQLite database is initialised by `database.py`. A full entity-relationship discussion is in [`docs/database_schema.md`](docs/database_schema.md).

| Table | Purpose |
|-------|---------|
| `Customers` | Unique Telegram users who place orders |
| `Runners`   | Telegram users who accept deliveries |
| `Orders`    | Order metadata & status lifecycle |

---

## Project Structure
```text
├── bot.py              # Main Telegram bot logic
├── database.py         # SQLite initialisation & helper
├── requirements.txt
├── data/
│   ├── makanApa.db     # Generated database file
│   ├── order_counter.json
│   └── devlist.json    # Optional allowlist for testers
└── docs/               # Additional project documentation
```

---

## Development
1. Enable debug logging by exporting `LOG_LEVEL=DEBUG` (see `logging.basicConfig`).
2. Run unit tests (coming soon) with `pytest`.
3. Follow [PEP 8](https://peps.python.org/pep-0008/) & type-hint all new functions.
4. Commit using conventional commits e.g. `feat: add refund flow`.

---

## Deployment Guide
The bot can be deployed anywhere that supports long-running Python processes:

• **Systemd service** – copy `systemd/makanApa.service` example.
• **Docker** – build the image: `docker build -t makanapa . && docker run …`.
• **Heroku / Render / Fly.io** – make sure to add the environment variables and enable continuous deployment from GitHub.

See `docs/deployment.md` for step-by-step instructions.

---

## Troubleshooting
• `telegram.error.NetworkError: Timed out` → Check internet connectivity or proxy.
• `Unauthorized: Error 401` → Ensure `BOT_TOKEN` is correct.
• `sqlite3.OperationalError: database is locked` → Make sure only one instance is writing to the DB.

---

## Contributing
Pull requests are welcome! Please:
1. Fork the repository & create a topic branch.
2. Write descriptive commit messages.
3. Ensure `pre-commit` hooks pass (`black`, `isort`, `flake8`).
4. Open a PR targeting `main` & fill out the template.

---

## License
Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
