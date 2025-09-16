import discord
import logging
from discord import app_commands
from box import Box
AUTO_ARCHIVE_DURATION = 10080  # 7 days

logger = logging.getLogger(__name__)

@app_commands.describe(
    driver1="First driver to blame",
    driver2="Second driver to blame",
    driver3="Optional third driver",
    driver4="Optional fourth driver",
    driver5="Optional fifth driver",
)
async def create_incident_poll(
    interaction: discord.Interaction,
    driver1: discord.User,
    driver2: discord.User,
    driver3: discord.User = None,
    driver4: discord.User = None,
    driver5: discord.User = None,
):
    try:
        await interaction.response.defer(ephemeral=True, thinking=True)

        users = [u for u in [driver1, driver2, driver3, driver4, driver5] if u is not None]
        logger.info("Creating incident poll for users %s", users)

        thread = await interaction.channel.create_thread(
            name=f"🚨 Incident Poll: {', '.join(u.display_name for u in users)}",
            type=discord.ChannelType.public_thread,
            auto_archive_duration=AUTO_ARCHIVE_DURATION
        )

        emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '🏁']  # add 🏁 emoji for racing incident
        poll_text = "🕵️ **Who is responsible for the incident?** React to vote:\n\n"

        # List users with numbered emojis
        for i, user in enumerate(users):
            poll_text += f"{emojis[i]} {user.mention}\n"

        # Add final option for racing incident
        poll_text += f"{emojis[-1]} Racing Incident\n"

        poll_message = await thread.send(poll_text)

        # Add reactions for all drivers
        for i in range(len(users)):
            await poll_message.add_reaction(emojis[i])

        # Add final reaction for racing incident
        await poll_message.add_reaction(emojis[-1])

        # 🔁 New follow-up message requesting video evidence
        driver_mentions = " ".join(user.mention for user in users)
        await thread.send(
            f"🎥 {driver_mentions} and spectators: Please reply to this thread with any available **video evidence** of the incident."
        )

        await interaction.followup.send(
            f"Incident poll created in {thread.mention}!", ephemeral=True
        )
    except Exception as e:
        logger.exception("Error running %s command in channel %s in guild %s", __name__, config.bot.channel, guild.name)
