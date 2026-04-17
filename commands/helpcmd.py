import discord
from discord import app_commands
from discord.ext import commands


class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Shows all available bot commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="🎮 Valorant Stats Tracker — Commands",
            description="Track your stats and compete with your friends.",
            color=0xFF4655
        )
        embed.add_field(name="/stats",
            value="Look up a player's rank, KD, ACS, ADR and recent matches.\n`/stats mofe#000`",
            inline=False)
        embed.add_field(name="/compare",
            value="Compare two players head to head with ▲ highlighting the winner.\n`/compare mofe#000 TenZ#00005`",
            inline=False)
        embed.add_field(name="/leaderboard-add",
            value="Register your Valorant account to this server's leaderboard.\n`/leaderboard-add mofe#000`",
            inline=False)
        embed.add_field(name="/leaderboard",
            value="See everyone's rank on this server's leaderboard.\n`/leaderboard`",
            inline=False)
        embed.add_field(name="/help", value="Shows this message.", inline=False)
        embed.set_footer(text="Valorant Stats Tracker  ·  reng.ar")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
