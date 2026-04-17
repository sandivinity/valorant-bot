"""
commands/stats.py — /stats command.
Now fetches full match details: map, agent, K/D/A, W/L, round score.
"""

import discord
from discord import app_commands
from discord.ext import commands

from utils.api import get_mmr, get_stats, get_recent_matches_detailed
from utils.embeds import build_stats_embed, build_error_embed


class StatsCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="stats",
        description="Look up Valorant stats — type Name#Tag like mofe#000"
    )
    @app_commands.describe(player="Your Riot ID e.g. mofe#000")
    async def stats(self, interaction: discord.Interaction, player: str):
        await interaction.response.defer(ephemeral=False)

        if "#" not in player:
            await interaction.followup.send(embed=build_error_embed(
                "Wrong format", "Use **Name#Tag**\nExample: `/stats mofe#000`"
            ))
            return

        name, tag = player.split("#", 1)
        name, tag = name.strip(), tag.strip()

        mmr = await get_mmr(name, tag)

        if not mmr:
            await interaction.followup.send(embed=build_error_embed(
                "Player Not Found",
                f"Couldn't find **{name}#{tag}**\n\n"
                f"• Check spelling — it's case-sensitive\n"
                f"• Use Name#Tag format\n"
                f"• Example: `/stats mofe#000`"
            ))
            return

        # Fetch stats and full match details concurrently
        import asyncio
        stats, matches = await asyncio.gather(
            get_stats(name, tag),
            get_recent_matches_detailed(name, tag, count=5)
        )

        embed = build_stats_embed(mmr, stats or {}, matches or [])
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(StatsCog(bot))
