"""
commands/compare.py — /compare command, improved visual design.
Winner of each stat gets a ✅, loser gets ❌, ties get ➖.
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from utils.api import get_mmr, get_stats
from utils.embeds import build_error_embed, RANK_EMOJIS, get_rank_color

RANK_ORDER = [
    "unranked",
    "iron 1", "iron 2", "iron 3",
    "bronze 1", "bronze 2", "bronze 3",
    "silver 1", "silver 2", "silver 3",
    "gold 1", "gold 2", "gold 3",
    "platinum 1", "platinum 2", "platinum 3",
    "diamond 1", "diamond 2", "diamond 3",
    "ascendant 1", "ascendant 2", "ascendant 3",
    "immortal 1", "immortal 2", "immortal 3",
    "radiant"
]


def rank_index(rank: str) -> int:
    return RANK_ORDER.index(rank.lower()) if rank.lower() in RANK_ORDER else 0


def stat_row(label: str, val1, val2) -> tuple[str, str, str]:
    """
    Returns (label, p1_display, p2_display) with win/lose/tie indicators.
    ✅ = winner  ❌ = loser  ➖ = tie
    """
    try:
        f1, f2 = float(val1), float(val2)
        if f1 > f2:
            return label, f"✅  {val1}", f"❌  {val2}"
        elif f2 > f1:
            return label, f"❌  {val1}", f"✅  {val2}"
        else:
            return label, f"➖  {val1}", f"➖  {val2}"
    except (ValueError, TypeError):
        return label, str(val1), str(val2)


class CompareCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="compare",
        description="Compare two Valorant players head to head"
    )
    @app_commands.describe(
        player1="First player's Riot ID e.g. mofe#000",
        player2="Second player's Riot ID e.g. TenZ#00005"
    )
    async def compare(self, interaction: discord.Interaction, player1: str, player2: str):
        await interaction.response.defer(ephemeral=False)

        for p in [player1, player2]:
            if "#" not in p:
                await interaction.followup.send(embed=build_error_embed(
                    "Wrong format", f"**{p}** — use Name#Tag format."
                ))
                return

        name1, tag1 = [x.strip() for x in player1.split("#", 1)]
        name2, tag2 = [x.strip() for x in player2.split("#", 1)]

        (mmr1, stats1), (mmr2, stats2) = await asyncio.gather(
            asyncio.gather(get_mmr(name1, tag1), get_stats(name1, tag1)),
            asyncio.gather(get_mmr(name2, tag2), get_stats(name2, tag2)),
        )

        if not mmr1:
            await interaction.followup.send(embed=build_error_embed("Not Found", f"Couldn't find **{name1}#{tag1}**"))
            return
        if not mmr2:
            await interaction.followup.send(embed=build_error_embed("Not Found", f"Couldn't find **{name2}#{tag2}**"))
            return

        rank1 = mmr1.get("rank", "Unranked")
        rank2 = mmr2.get("rank", "Unranked")
        s1    = stats1 or {}
        s2    = stats2 or {}

        e1 = RANK_EMOJIS.get(rank1.split()[0] if rank1 else "Unranked", "❓")
        e2 = RANK_EMOJIS.get(rank2.split()[0] if rank2 else "Unranked", "❓")

        # Rank winner
        r1i, r2i = rank_index(rank1), rank_index(rank2)
        if r1i > r2i:
            rank1_str, rank2_str = f"✅  {rank1}", f"❌  {rank2}"
        elif r2i > r1i:
            rank1_str, rank2_str = f"❌  {rank1}", f"✅  {rank2}"
        else:
            rank1_str, rank2_str = f"➖  {rank1}", f"➖  {rank2}"

        # Stat rows
        rows = [
            stat_row("KD",    s1.get("kd",      0), s2.get("kd",      0)),
            stat_row("ACS",   s1.get("acs",      0), s2.get("acs",     0)),
            stat_row("ADR",   s1.get("adr",      0), s2.get("adr",     0)),
            stat_row("Games", s1.get("matches",  0), s2.get("matches", 0)),
        ]

        # Who won overall — count ✅ each player has
        wins1 = sum(1 for _, v1, _ in rows if v1.startswith("✅"))
        wins2 = sum(1 for _, _, v2 in rows if v2.startswith("✅"))
        if r1i > r2i: wins1 += 1
        elif r2i > r1i: wins2 += 1

        if wins1 > wins2:
            overall = f"🏆 **{name1}#{tag1}** wins overall ({wins1} vs {wins2})"
        elif wins2 > wins1:
            overall = f"🏆 **{name2}#{tag2}** wins overall ({wins2} vs {wins1})"
        else:
            overall = f"🤝 It's a tie! ({wins1} vs {wins2})"

        # Build embed
        embed = discord.Embed(
            title=f"⚔️  {name1}#{tag1}  vs  {name2}#{tag2}",
            description=overall,
            color=get_rank_color(rank1)
        )

        # Header row
        embed.add_field(name="​",      value=f"**{e1} {name1}#{tag1}**", inline=True)
        embed.add_field(name="​",      value="​",                         inline=True)
        embed.add_field(name="​",      value=f"**{e2} {name2}#{tag2}**", inline=True)

        # Rank
        embed.add_field(name="Rank",   value=f"```{rank1_str}```", inline=True)
        embed.add_field(name="​",      value="​",                   inline=True)
        embed.add_field(name="Rank",   value=f"```{rank2_str}```", inline=True)

        # Stats
        for label, v1, v2 in rows:
            embed.add_field(name=label, value=f"```{v1}```", inline=True)
            embed.add_field(name="​",   value="​",            inline=True)
            embed.add_field(name=label, value=f"```{v2}```", inline=True)

        embed.set_footer(text="Valorant Stats Tracker  ·  reng.ar")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CompareCog(bot))
