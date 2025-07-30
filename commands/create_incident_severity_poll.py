# from discord.ext import commands
# from discord import app_commands

# @incident_group.command(name="severity", description="Create a severity poll on an existing incident thread.")
# async def severity(
#         interaction: discord.Interaction,
# ):
#     await interaction.response.defer()

#     # Ensure the command is run inside a thread
#     if not isinstance(interaction.channel, discord.Thread):
#         await interaction.followup.send("This command must be used inside an incident thread.")
#         return

#     severity_options = [
#         "No Further Action",
#         "Warning",
#         "1-Place Grid Penalty",
#         "3-Place Grid Penalty",
#         "5-Place Grid Penalty",
#         "1 Race Ban"
#     ]

#     emojis = ['✅', '⚠️', '1️⃣', '3️⃣', '5️⃣', '❌']
#     msg = "**🔨 Vote on penalty severity:**\n\n" + "\n".join(
#         f"{emoji} {option}" for emoji, option in zip(emojis, severity_options)
#     )

#     vote_msg = await interaction.channel.send(msg)

#     for emoji in emojis:
#         await vote_msg.add_reaction(emoji)

#     await interaction.followup.send(f"Severity poll created in incident {interaction.channel.mention}.")