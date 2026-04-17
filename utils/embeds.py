"""
utils/embeds.py — Builds Discord embeds. Agent names now resolved via cache.
"""

import discord
from datetime import datetime

RANK_COLORS = {
    "Iron": 0x8B7355, "Bronze": 0xCD7F32, "Silver": 0xC0C0C0,
    "Gold": 0xFFD700, "Platinum": 0x00CED1, "Diamond": 0xB044FF,
    "Ascendant": 0x00FF7F, "Immortal": 0xFF4040, "Radiant": 0xFFE566,
    "Unranked": 0x808080,
}
RANK_EMOJIS = {
    "Iron": "🪨", "Bronze": "🥉", "Silver": "🥈", "Gold": "🥇",
    "Platinum": "💎", "Diamond": "💠", "Ascendant": "🌿",
    "Immortal": "🔥", "Radiant": "⚡", "Unranked": "❓",
}
AGENT_EMOJIS = {
    "Jett": "💨", "Reyna": "👁️", "Phoenix": "🔥", "Yoru": "👻",
    "Neon": "⚡", "Iso": "🔮", "Sage": "💚", "Skye": "🌿",
    "Breach": "💥", "Sova": "🏹", "KAYO": "🤖", "KAY/O": "🤖",
    "Fade": "🌑", "Gekko": "🦎", "Viper": "☠️", "Brimstone": "💣",
    "Astra": "⭐", "Omen": "👁️", "Harbor": "🌊", "Clove": "🍀",
    "Killjoy": "⚙️", "Cypher": "🕵️", "Chamber": "🎩",
    "Deadlock": "🔒", "Raze": "💥", "Vyse": "🕸️",
}
MAP_NAMES = {
    "pitt": "Pearl", "jam": "Lotus", "juliett": "Abyss",
    "triad": "Haven", "duality": "Bind", "bonsai": "Split",
    "port": "Icebox", "ascent": "Ascent", "foxtrot": "Breeze",
    "canyon": "Fracture", "range": "The Range", "poveglia": "Sunset",
}


def clean_map_name(raw: str) -> str:
    key = raw.strip("/").split("/")[-1].lower()
    return MAP_NAMES.get(key, raw.split("/")[-1].capitalize())


def get_rank_color(rank: str) -> int:
    for tier, color in RANK_COLORS.items():
        if tier.lower() in rank.lower():
            return color
    return 0x808080


def build_stats_embed(mmr: dict, stats: dict, matches: list) -> discord.Embed:
    name   = mmr.get("name", "Unknown")
    tag    = mmr.get("tag", "0000")
    rank   = mmr.get("rank", "Unranked")
    region = mmr.get("region", "?").upper()
    color  = get_rank_color(rank)
    emoji  = RANK_EMOJIS.get(rank.split()[0] if rank else "Unranked", "❓")

    embed = discord.Embed(title=f"{emoji}  {name}#{tag}", color=color, timestamp=datetime.utcnow())

    embed.add_field(name="Rank",   value=f"```{rank}```",   inline=True)
    embed.add_field(name="Region", value=f"```{region}```", inline=True)
    embed.add_field(name="\u200b", value="\u200b",          inline=True)

    if stats:
        embed.add_field(name="KD",  value=f"```{stats.get('kd',  'N/A')}```", inline=True)
        embed.add_field(name="ACS", value=f"```{stats.get('acs', 'N/A')}```", inline=True)
        embed.add_field(name="ADR", value=f"```{stats.get('adr', 'N/A')}```", inline=True)
        k, d, a = stats.get("kills", 0), stats.get("deaths", 0), stats.get("assists", 0)
        embed.add_field(name="K / D / A",    value=f"```{k} / {d} / {a}```",          inline=True)
        embed.add_field(name="Ranked Games", value=f"```{stats.get('matches', 0)}```", inline=True)
        embed.add_field(name="\u200b",       value="\u200b",                           inline=True)

    if matches:
        wins  = sum(1 for m in matches if m["won"])
        total = len(matches)
        wr    = round((wins / total) * 100) if total else 0
        lines = []
        for m in matches:
            result      = "🟢" if m["won"] else "🔴"
            map_display = clean_map_name(m["map"])
            score_str   = f" `{m['round_score']}`" if m.get("round_score") else ""
            agent       = m.get("agent", "Unknown")
            agent_emoji = AGENT_EMOJIS.get(agent, "🎮")
            kda         = f"{m['kills']}/{m['deaths']}/{m['assists']}"
            lines.append(f"{result} **{map_display}**{score_str}  {agent_emoji} {agent}  `{kda}`  KD {m['kd']}")

        embed.add_field(
            name=f"Recent Matches  ·  {wins}W {total-wins}L  ·  {wr}% WR",
            value="\n".join(lines),
            inline=False
        )

    embed.set_footer(text="Valorant Stats Tracker  ·  reng.ar")
    return embed


def build_error_embed(title: str, description: str) -> discord.Embed:
    return discord.Embed(
        title=f"❌  {title}", description=description, color=0xFF4040, timestamp=datetime.utcnow()
    ).set_footer(text="Example: /stats mofe#000")
