import discord
from discord import app_commands
import jobs

@app_commands.describe(
    job_name="The name of the job to execute.",
)
@app_commands.choices(
    job_name=[
        app_commands.Choice(name="Finalise Polls", value="finalise_polls")
    ]
)
async def run_job(
        interaction: discord.Interaction,
        job_name: str = None,
):
    await interaction.response.defer()
    job = getattr(jobs, job_name)

    await job(interaction.client, interaction.client.config)

    await interaction.followup.send(
        f"Ran job {job_name}.", ephemeral=True
    )

