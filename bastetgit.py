import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime
import json
import pytz
import os

# -----------------------------
# CONFIGURATION SECTION
# -----------------------------
# Guild-specific ID for testing or deployment (replace with your own server ID)
GUILD_ID = 1364563721086832650
# Register the guild object for per-guild slash command sync
guild = discord.Object(id=GUILD_ID)

# Bot initialization with default intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
reminders_file = "reminders.json"
scrim_attendance = {}

# -----------------------------
# UI CLASS: ScheduleView
# -----------------------------
# Handles RSVP buttons for scrim messages
class ScheduleView(discord.ui.View):
    def __init__(self, message_id):
        super().__init__(timeout=None)
        self.message_id = message_id

    @discord.ui.button(label="✅ I can make it", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        scrim_attendance.setdefault(self.message_id, {'yes': set(), 'no': set()})
        scrim_attendance[self.message_id]['yes'].add(interaction.user.display_name)
        scrim_attendance[self.message_id]['no'].discard(interaction.user.display_name)
        await self.update_embed(interaction)

    @discord.ui.button(label="❌ I can't", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        scrim_attendance.setdefault(self.message_id, {'yes': set(), 'no': set()})
        scrim_attendance[self.message_id]['no'].add(interaction.user.display_name)
        scrim_attendance[self.message_id]['yes'].discard(interaction.user.display_name)
        await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        yes_list = ", ".join(scrim_attendance[self.message_id]['yes']) or "No one yet"
        no_list = ", ".join(scrim_attendance[self.message_id]['no']) or "No one yet"

        embed = interaction.message.embeds[0]
        embed.set_field_at(2, name="✅ Warriors Attending", value=yes_list, inline=False)
        embed.set_field_at(3, name="❌ Cannot Attend", value=no_list, inline=False)
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.defer()

# -----------------------------
# EVENT: on_ready
# -----------------------------
@bot.event
async def on_ready():
    await bot.tree.sync(guild=guild)
    print(f"Bastet synced {len(await bot.tree.fetch_commands(guild=guild))} slash commands to guild {guild.id}.")
    print(f"Bastet is online as {bot.user}")

    guild_name = bot.guilds[0].name if bot.guilds else "NXRI"
    activity = discord.Activity(type=discord.ActivityType.watching, name=f"over {guild_name} scrims 🐾")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    if not check_reminders.is_running():
        check_reminders.start()

# -----------------------------
# /scrim Command
# -----------------------------
# Schedule a new scrim announcement
@bot.tree.command(name="scrim", description="Summon Bastet to schedule a new scrim", guild=guild)
@app_commands.describe(opponent="Opponent team name", date="Date (YYYY-MM-DD)", time="Time (24h CST)")
async def scrim(interaction: discord.Interaction, opponent: str, date: str, time: str):
    try:
        datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        server_name = interaction.guild.name if interaction.guild else "this server"

        embed = discord.Embed(
            title=f"🌙 Bastet Declares a Scrim vs {opponent}",
            description=f"🗓️ **Date:** `{date}`\n⏰ **Time:** `{time}` CST",
            color=discord.Color.gold()
        )
        embed.add_field(name="🌚 Challengers", value=opponent, inline=False)
        embed.add_field(name="📜 Divine Message", value=f"\"Mark your loyalty below, warriors of {server_name}.\"", inline=False)
        embed.add_field(name="✅ Warriors Attending", value="No one yet", inline=False)
        embed.add_field(name="❌ Cannot Attend", value="No one yet", inline=False)
        embed.set_footer(text=f"{server_name} • Protected by Bastet")

        message = await interaction.channel.send(embed=embed, view=ScheduleView(interaction.id))
        await interaction.response.send_message("📖 Scrim scroll summoned by Bastet.", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("⚠️ Invalid date/time format. Use `YYYY-MM-DD` and `HH:MM` (24h CST).", ephemeral=True)

# -----------------------------
# /setreminder Command
# -----------------------------
# Set a one-time, daily, or weekly reminder
@bot.tree.command(name="setreminder", description="Set a daily, weekly, or one-time reminder", guild=guild)
@app_commands.describe(time="Time in HH:MM EST", type="Reminder type", message="Reminder text", day="Day of the week (for weekly)", roles="Role IDs (comma separated)")
async def setreminder(interaction: discord.Interaction, time: str, type: str, message: str, day: str = None, roles: str = None):
    try:
        datetime.strptime(time, "%H:%M")
        reminder = {
            "type": type,
            "time": time,
            "message": message,
            "day": day.lower() if day else None,
            "roles": [r.strip() for r in roles.split(",")] if roles else [],
            "channel": interaction.channel.id,
            "guild": interaction.guild_id
        }

        data = []
        if os.path.exists(reminders_file):
            with open(reminders_file, "r") as f:
                data = json.load(f)

        data.append(reminder)
        with open(reminders_file, "w") as f:
            json.dump(data, f, indent=2)

        await interaction.response.send_message(f"✅ Reminder set for {time} EST ({type})", ephemeral=True)
    except ValueError:
        await interaction.response.send_message("⚠️ Invalid time format. Use `HH:MM` (24h format).", ephemeral=True)

# -----------------------------
# /reminders Command
# -----------------------------
# View and delete active reminders
@bot.tree.command(name="reminders", description="View and delete active reminders", guild=guild)
async def reminders(interaction: discord.Interaction):
    if not os.path.exists(reminders_file):
        await interaction.response.send_message("No reminders found.", ephemeral=True)
        return

    with open(reminders_file, "r") as f:
        data = json.load(f)

    server_data = [r for r in data if r.get("guild") == interaction.guild_id]
    if not server_data:
        await interaction.response.send_message("No reminders set for this server.", ephemeral=True)
        return

    options = [
        discord.SelectOption(
            label=f"{r['type']} - {r['time']} - {r['message'][:30]}",
            value=str(i)
        ) for i, r in enumerate(server_data)
    ]

    class ReminderSelect(discord.ui.View):
        @discord.ui.select(placeholder="Select a reminder to delete", options=options)
        async def select_callback(self, interaction2: discord.Interaction, select: discord.ui.Select):
            index = int(select.values[0])
            deleted = server_data.pop(index)

            data[:] = [r for r in data if r != deleted]
            with open(reminders_file, "w") as f:
                json.dump(data, f, indent=2)

            await interaction2.response.send_message(f"Deleted reminder: {deleted['message']}", ephemeral=True)

    await interaction.response.send_message("Choose a reminder to delete:", view=ReminderSelect(), ephemeral=True)

# -----------------------------
# Reminder Checker Loop
# -----------------------------
# This task runs every minute and checks reminders
@tasks.loop(minutes=1)
async def check_reminders():
    now = datetime.now(pytz.timezone("US/Eastern"))
    current_time = now.strftime("%H:%M")
    current_day = now.strftime("%A").lower()

    if not os.path.exists(reminders_file):
        return

    with open(reminders_file, "r") as f:
        data = json.load(f)

    for reminder in data[:]:
        if reminder["time"] != current_time:
            continue

        if reminder["type"] == "once":
            data.remove(reminder)
        elif reminder["type"] == "weekly" and reminder["day"] != current_day:
            continue

        channel = bot.get_channel(reminder["channel"])
        if not channel:
            continue

        role_mentions = " ".join([f"<@&{rid}>" for rid in reminder["roles"]])
        await channel.send(f"{role_mentions} 🗓️ {reminder['message']}")

    with open(reminders_file, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# Run Bastet
# -----------------------------
bot.run("YOUR_BOT_TOKEN")



#THIS BOT IS MADE BY TAY (NYUDACREATOR)