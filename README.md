# GitHub Notification Discord Bot 🤖🔔

A Discord bot that sends real-time GitHub repository updates to your Discord channel, including commits, pull requests, and more.

## Features ✨

- ✅ Push notifications with commit details
- ✅ Pull request status updates
- ✅ Repository activity tracking
- ✅ Customizable embed messages
- ✅ Secure webhook verification

## Setup Guide 🛠️

### Prerequisites

- Python 3.10+
- Discord bot token ([Get one here](https://discord.com/developers/applications))
- GitHub repository admin access

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Mohabdo21/discord-github-bot.git
   cd discord-github-bot
   ```

2. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your credentials:
   ```env
   TOKEN=your_discord_bot_token
   GITHUB_NOTIFICATION_CHANNEL=your_discord_channel_id
   GITHUB_WEBHOOK_SECRET=your_github_webhook_secret
   ```

### Running the Bot

```bash
python main.py
```

## Deployment 🚀

Host your bot 24/7 using:

- [Render](https://render.com) (Recommended for beginners)
- [Fly.io](https://fly.io) (Free tier available)
- [Railway](https://railway.app) (GitHub integration)

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## Configuration ⚙️

| Variable                      | Description                        |
| ----------------------------- | ---------------------------------- |
| `TOKEN`                       | Discord bot token                  |
| `GITHUB_NOTIFICATION_CHANNEL` | Channel ID for notifications       |
| `GITHUB_WEBHOOK_SECRET`       | GitHub webhook secret for security |
