import os
import discord
from discord.ext import commands
from discord import app_commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import commands as command_functions
import importlib
import jobs as job_functions
from box import Box
import pytz
import yaml

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

async def register_commands(config, bot):
    try:
        # Register commands
        groups = {
            group_name: app_commands.Group(name=group_name, description=group_name.upper())
            for group_name in [command.group for command in config.bot.commands]
        }

        for command_config in config.bot.commands:
            func = getattr(command_functions, command_config.func_name)
            command_instance = groups.get(command_config.group).command(name=command_config.name, description=command_config.description)(func)
            print(f"Added {command_config.name} command ({command_config.description}).")

        for group in groups.values():
            bot.tree.add_command(group)

        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"Error syncing commands: {e}")

def register_jobs(config):
    timezone = pytz.timezone(config.bot.timezone)
    scheduler = AsyncIOScheduler(timezone=timezone)

    # Register cron jobs
    for job_config in config.bot.jobs:
        trigger = CronTrigger.from_crontab(job_config.interval)
        func = getattr(job_functions, job_config.func_name)
        job_instance = scheduler.add_job(func, trigger, args=[bot, config])
        print(f"Scheduled {job_config.name} job ({job_config.description}). Next run time at {job_instance.trigger.get_next_fire_time(None, datetime.now(timezone))}.")
        
    if not scheduler.running:
        scheduler.start()

@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")

    print(f"Reading config")
    # Try read config
    with open("config.yml", "r") as f:
        config = Box(yaml.safe_load(f))

    await register_commands(config, bot)
    register_jobs(config)
    print("Ready.")

if __name__ == "__main__":
    bot.run(TOKEN)