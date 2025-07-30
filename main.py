import os
import discord
from discord.ext import commands
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from commands import create_incident_poll
from jobs import close_incident_threads_and_post_summaries
import pytz


TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)
incident_group = app_commands.Group(name="incident", description="Commands related to an incident")

scheduler = AsyncIOScheduler(timezone=pytz.timezone('Australia/Melbourne'))

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")
    try:
        # Register commands
        create_incident_poll_command = incident_group.command(name="create_poll", description="Create an incident poll between up to 5 drivers.")(create_incident_poll)
        bot.tree.add_command(incident_group)
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    if not scheduler.running:
        scheduler.start()

    # Register cron jobs    
    trigger = CronTrigger(second="*/10")
    scheduler.add_job(close_incident_threads_and_post_summaries, trigger, args=[bot])
    print("Scheduled thread closure task.")

if __name__ == "__main__":
    bot.run(TOKEN)