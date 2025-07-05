# Deployment Guide

This guide outlines a few common ways to deploy the **makanApa** bot. Feel free to adapt to your own hosting provider.

---

## 1. Systemd (Generic Linux VPS)
1. Copy the sample service file.
    ```bash
    sudo cp systemd/makanApa.service /etc/systemd/system/
    ```
2. Update the `WorkingDirectory` and environment variables in the service file.
3. Start the service and enable auto-start on boot:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable --now makanApa
    sudo journalctl -u makanApa -f  # view logs
    ```

---

## 2. Docker
1. Build the image:
    ```bash
    docker build -t makanapa .
    ```
2. Run the container:
    ```bash
    docker run -d --name makanapa \
        -e BOT_TOKEN="$BOT_TOKEN" \
        -e RUNNER_GROUP_ID="$RUNNER_GROUP_ID" \
        -v $(pwd)/data:/app/data \
        makanapa
    ```

---

## 3. Render.com
1. Create a new "Web Service" with **Python** as the environment.
2. Point it to your Git repository.
3. Set the build & start commands:
    * **Build:** `pip install -r requirements.txt && python database.py`
    * **Start:** `python bot.py`
4. Add the two environment variables under *Environment → Secret Files*.

---

## 4. Fly.io
1. Install the [Fly CLI](https://fly.io/docs/hands-on/install-flyctl/).
2. Run `fly launch` and follow the prompts.
3. Set secrets:
    ```bash
    fly secrets set BOT_TOKEN=$BOT_TOKEN RUNNER_GROUP_ID=$RUNNER_GROUP_ID
    ```
4. Deploy:
    ```bash
    fly deploy
    ```

---

### Tips
• Keep the `data/` volume persistent (Docker bind-mount or Fly volume) so orders survive restarts.
• Monitor logs and Telegram’s status page for downtime.
• Use a supervisor like `systemd` or `pm2` to auto-restart on failure.