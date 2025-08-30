# Bastet-Discord-Bot
 Discord Bot Made by NyuDaCreator--
# 🐾 Bastet - Discord Scrim Scheduler Bot

Bastet is a powerful scheduling assistant for Discord esports teams. She allows you to schedule scrims, track attendance with buttons, and automate reminders—all through elegant slash commands.

## 🔧 Features

- `/scrim` – Create a scrim with opponent name, date, and time
- `/setreminder` – Schedule daily, weekly, or one-time reminders
- `/reminders` – View and delete active reminders
- Attendance tracking via reaction buttons ✅ ❌
- Server-aware (reminders only show in your server)
- Dynamic bot presence based on server name

## 🚀 Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/bastet-bot.git
   cd bastet-bot
2. Create a Virtual Environment:
    python3 -m venv bastet-env
source bastet-env/bin/activate  # On Windows: bastet-env\Scripts\activate

3. Install dependencies(on Powershell[Admin]):
   pip install -r requirements.txt
4. Set your bot token in the bastet.py file(It's at the bottom):
   bot.run("YOUR_DISCORD_BOT_TOKEN")
5. Run the bot:
   Python bastetgit.py
