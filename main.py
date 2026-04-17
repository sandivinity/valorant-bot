"""
main.py — Bot entry point.
Initializes the SQLite database and agent cache on startup.
"""

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

    from utils.api import load_agent_cache
    from utils.database import init_db

    await init_db()           # Set up SQLite tables
    await load_agent_cache()  # Load agent UUID → name map

    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


async def load_cogs():
    cog_files = [
        "commands.stats",
        "commands.leaderboard",
        "commands.helpcmd",
        "commands.compare",
    ]
    for cog in cog_files:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded: {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")


async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
