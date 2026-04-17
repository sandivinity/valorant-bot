"""
commands/leaderboard.py — Leaderboard commands using SQLite.
Switched from JSON file to a real database — cleaner, safer, more scalable.
"""

import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime

from utils.api import get_mmr
from utils.embeds import build_error_embed, RANK_EMOJIS
from utils.database import add_player, get_players, remove_player


class LeaderboardCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ── /leaderboard-add ──────────────────────────────────────────────────────
    @app_commands.command(
        name="leaderboard-add",
        description="Register your Valorant account to this server's leaderboard"
    )
    @app_commands.describe(player="Your Riot ID e.g. mofe#000")
    async def leaderboard_add(self, interaction: discord.Interaction, player: str):
        await interaction.response.defer(ephemeral=True)

        if "#" not in player:
            await interaction.followup.send(
                embed=build_error_embed("Wrong format", "Use **Name#Tag** e.g. `mofe#000`"),
                ephemeral=True
            )
            return

        name, tag = [x.strip() for x in player.split("#", 1)]

        # Verify the account exists before adding
        mmr = await get_mmr(name, tag)
        if not mmr:
            await interaction.followup.send(
                embed=build_error_embed("Player Not Found", f"Couldn't find **{name}#{tag}**"),
                ephemeral=True
            )
            return

        # Save to database — one line instead of load/modify/save JSON
        await add_player(
            server_id    = str(interaction.guild_id),
            user_id      = str(interaction.user.id),
            discord_name = str(interaction.user),
            val_name     = name,
            val_tag      = tag
        )

        rank = mmr.get("rank", "Unranked")
        embed = discord.Embed(
            title="✅ Added to Leaderboard!",
            description=f"**{name}#{tag}** registered.\nCurrent rank: **{rank}**",
            color=0x57F287
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ── /leaderboard-remove ───────────────────────────────────────────────────
    @app_commands.command(
        name="leaderboard-remove",
        description="Remove yourself from this server's leaderboard"
    )
    async def leaderboard_remove(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        await remove_player(str(interaction.guild_id), str(interaction.user.id))

        embed = discord.Embed(
            title="✅ Removed",
            description="You've been removed from this server's leaderboard.",
            color=0x57F287
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    # ── /leaderboard ──────────────────────────────────────────────────────────
    @app_commands.command(
        name="leaderboard",
        description="See the Valorant rank leaderboard for this server"
    )
    async def leaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)

        server_id = str(interaction.guild_id)

        # Read from database — returns list of dicts
        players = await get_players(server_id)

        if not players:
            embed = discord.Embed(
                title="📋 Server Leaderboard",
                description="No one registered yet!\nUse `/leaderboard-add` to join.",
                color=0x5865F2
            )
            await interaction.followup.send(embed=embed)
            return

        # Fetch current rank for each player
        ranked = []
        for p in players:
            mmr  = await get_mmr(p["val_name"], p["val_tag"])
            rank = mmr.get("rank", "Unranked") if mmr else "Unranked"
            ranked.append({**p, "rank": rank})

        # Sort by rank tier (higher = better)
        rank_order = [
            "radiant", "immortal 3", "immortal 2", "immortal 1",
            "ascendant 3", "ascendant 2", "ascendant 1",
            "diamond 3", "diamond 2", "diamond 1",
            "platinum 3", "platinum 2", "platinum 1",
            "gold 3", "gold 2", "gold 1",
            "silver 3", "silver 2", "silver 1",
            "bronze 3", "bronze 2", "bronze 1",
            "iron 3", "iron 2", "iron 1", "unranked"
        ]

        def rank_key(p):
            r = p["rank"].lower()
            return rank_order.index(r) if r in rank_order else len(rank_order)

        ranked.sort(key=rank_key)

        medals = ["🥇", "🥈", "🥉"]
        lines  = []
        for i, p in enumerate(ranked):
            pos        = medals[i] if i < 3 else f"`#{i+1}`"
            rank_emoji = RANK_EMOJIS.get(p["rank"].split()[0] if p["rank"] else "Unranked", "❓")
            lines.append(
                f"{pos} **{p['val_name']}#{p['val_tag']}** — {rank_emoji} {p['rank']}"
            )

        embed = discord.Embed(
            title="🏆 Server Valorant Leaderboard",
            description="\n".join(lines),
            color=0xFFD700,
            timestamp=datetime.utcnow()
        )
        embed.set_footer(text=f"{len(ranked)} player(s) · Valorant Stats Tracker")
        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))
