import logging
import string
import discord
from discord.ext import commands
import datetime

logger = logging.getLogger(__name__)

THREAD_SUMMARY_TEMPLATE = string.Template("""\
**Thread:** $thread_mention
$outcome (**$vote_count votes**) ($vote_emoji)

""")

FULL_SUMMARY_TEMPLATE = string.Template("""\
📊 **Weekly Incident Poll Summary for $channel_name**
📅 **Race Date:** $race_date

$thread_summaries
""")

def get_most_recent_tuesday(reference_date: datetime.date | None = None) -> str:
    """
    Returns the most recent Tuesday as a string in format DD/MM/YYYY.
    If reference_date is None, uses today's UTC date.
    """
    today = reference_date or datetime.datetime.now(datetime.timezone.utc).date()
    days_since_tuesday = (today.weekday() - 1) % 7  # Tuesday is weekday 1
    last_tuesday = today - datetime.timedelta(days=days_since_tuesday)
    return last_tuesday.strftime("%d/%m/%Y")


async def finalise_polls(bot: commands.Bot, config):
    guild = discord.utils.get(bot.guilds, name=config.bot.guild)
    review_channel = discord.utils.get(guild.text_channels, name=config.bot.channel)
    if not review_channel:
        logger.warning("No #%s channel found in guild %s", config.bot.channel, guild.name)
        return

    logger.info("Finalising polls in #%s in guild %s", review_channel.name, guild.name)

    thread_summaries = []
    try:
        threads = review_channel.threads
        for thread in threads:
            if thread.archived or thread.owner_id != bot.user.id:
                continue

            logger.info(
                "Finalising poll for thread %s in #%s in guild %s",
                thread.name, review_channel.name, guild.name
            )

            messages = [msg async for msg in thread.history(limit=1, oldest_first=True)]
            poll_msg = messages[0] if messages else None

            if poll_msg and poll_msg.reactions:
                emoji_to_label = {}
                for line in poll_msg.content.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split(' ', 1)
                    if len(parts) == 2:
                        emoji, label = parts
                        emoji_to_label[emoji] = label

                max_votes = 0
                max_vote_emoji = "🚫"
                outcome = "No votes placed."
                for reaction in poll_msg.reactions:
                    votes = reaction.count - 1 if reaction.count > 0 else 0
                    if votes > max_votes:
                        max_votes = votes
                        max_vote_emoji = reaction.emoji

                        if "Racing Incident" not in emoji_to_label[reaction.emoji]:
                            outcome = f"{emoji_to_label[reaction.emoji]} penalty"
                        else:
                            outcome = "Racing Incident - No penalties."

                thread_summary = THREAD_SUMMARY_TEMPLATE.substitute(
                    thread_mention=thread.mention,
                    outcome=outcome,
                    vote_count=max_votes,
                    vote_emoji=max_vote_emoji
                )
                logger.info("%s: %s", thread.name, thread_summary)
            else:
                logger.error(
                    "Unable to find poll or votes for thread %s in #%s in guild %s",
                    thread.name, review_channel.name, guild.name
                )
                thread_summary = f"**Thread:** {thread.mention}\nNo valid poll found.\n"

            thread_summaries.append(thread_summary)

            await thread.edit(archived=True, locked=True)

        if not thread_summaries:
            logger.info(
                "No active incident threads found this week in #%s in guild %s",
                review_channel.name, guild.name
            )
            thread_summaries.append("No active incident threads found this week.\n")

        full_summary = FULL_SUMMARY_TEMPLATE.substitute(
            channel_name=review_channel.mention,
            race_date=get_most_recent_tuesday(),
            thread_summaries="".join(thread_summaries),
        )

        logger.info(full_summary)
        await review_channel.send(full_summary)

    except Exception as e:
        logger.exception(
            "Error running %s job in #%s in guild %s",
            __name__, config.bot.channel, guild.name
        )
