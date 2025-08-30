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
    ```bash
    python3 -m venv bastet-env
    source bastet-env/bin/activate  # On Windows: bastet-env\Scripts\activate

3. Install dependencies(on Powershell[Admin]):
  ```Bash
   pip install -r requirements.txt
```
4. Set your bot token in the bastet.py file(It's at the bottom):
   ```
   bot.run("YOUR_DISCORD_BOT_TOKEN")
6. Run the bot:
   ```
   Python bastetgit.py


   Security

This bot is designed to:

Restrict command sync and reminders to a single server using your GUILD_ID.

Prevent global reminder sharing across servers.

Avoid exposing sensitive information in logs or bot replies.

 Deployment on EC2 (Optional)

Use tmux to keep Bastet running even after you close the SSH session:

tmux new -s bastet
python bastet.py


To detach:

Ctrl + B then D

 License

MIT License — free to use and modify.


---

## ✅ Steps to Add This to Your Repo

1. Create a new file in your repo called `README.md`
2. Paste the above markdown content
3. Edit the repo name, features, and description as needed
4. Push the file:

```bash
git add README.md
git commit -m "Added README with setup instructions"
git push origin main


Let me know if you want me to write the .gitignore, requirements.txt, or .env.example file too.
