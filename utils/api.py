"""
utils/api.py — All Valorant API calls using Rengar API (reng.ar).

AGENT UUID LOOKUP:
The Rengar API returns agent UUIDs instead of names (e.g. "b444168c-4e35...")
We fix this by fetching all agents from valorant-api.com on startup and caching them.
This is called "caching" — fetch once, reuse forever. It's a common performance pattern.
"""

import aiohttp
import asyncio

BASE_URL = "https://reng.ar/api"

# Module-level cache — populated once when load_agent_cache() is called
# Maps UUID (lowercase) → agent name e.g. "b444168c..." → "Jett"
AGENT_CACHE: dict[str, str] = {}


async def load_agent_cache():
    """
    Fetches all agents from valorant-api.com and builds a UUID → name dict.
    Call this once when the bot starts up (in main.py on_ready).
    After this, resolving any agent UUID is instant — no extra API calls needed.
    """
    url = "https://valorant-api.com/v1/agents?isPlayableCharacter=true"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    data = await r.json()
                    for agent in data.get("data", []):
                        uuid = agent.get("uuid", "").lower()
                        name = agent.get("displayName", "Unknown")
                        AGENT_CACHE[uuid] = name
                    print(f"✅ Agent cache loaded: {len(AGENT_CACHE)} agents")
                else:
                    print(f"⚠️  Failed to load agent cache: HTTP {r.status}")
    except Exception as e:
        print(f"⚠️  Agent cache error: {e}")


def resolve_agent(raw: str) -> str:
    """
    Converts a UUID or name to a display name.
    If it's already a name like "Jett", returns it as-is.
    If it's a UUID, looks it up in the cache.
    If not found, returns "Unknown".
    """
    if not raw:
        return "Unknown"
    # Check if it's in the cache (UUIDs are lowercase in the cache)
    looked_up = AGENT_CACHE.get(raw.lower())
    if looked_up:
        return looked_up
    # If not a UUID (no dashes), it's probably already a name
    if "-" not in raw:
        return raw
    return "Unknown"


async def get_mmr(name: str, tag: str) -> dict | None:
    url = f"{BASE_URL}/mmr/{name}/{tag}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.json() if r.status == 200 else None


async def get_stats(name: str, tag: str) -> dict | None:
    url = f"{BASE_URL}/stats/{name}/{tag}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.json() if r.status == 200 else None


async def get_match_history(name: str, tag: str) -> list | None:
    url = f"{BASE_URL}/matches/{name}/{tag}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            if r.status == 200:
                data = await r.json()
                return data.get("matches", [])
            return None


async def get_match_details(match_id: str) -> dict | None:
    url = f"{BASE_URL}/match/{match_id}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            return await r.json() if r.status == 200 else None


async def get_recent_matches_detailed(name: str, tag: str, count: int = 5) -> list:
    """
    Fetches match history then gets full details for each match concurrently.
    Resolves agent UUIDs to real names using the cache.
    """
    matches_list = await get_match_history(name, tag)
    if not matches_list:
        return []

    tasks = [get_match_details(m["id"]) for m in matches_list[:count]]
    results = await asyncio.gather(*tasks)

    processed = []
    for match_data in results:
        if not match_data:
            continue
        try:
            map_name = match_data.get("map", "Unknown")
            players  = match_data.get("players", [])
            teams    = match_data.get("teams", [])

            player_info = None
            for p in players:
                if p.get("name", "").lower() == name.lower():
                    player_info = p
                    break

            if not player_info:
                continue

            kills   = player_info.get("kills", 0)
            deaths  = player_info.get("deaths", 0)
            assists = player_info.get("assists", 0)
            team    = player_info.get("team", "")

            # Resolve agent UUID → real name using our cache
            raw_agent = player_info.get("agent", "")
            agent = resolve_agent(raw_agent)

            won = False
            for t in teams:
                if t.get("id", "").lower() == team.lower():
                    won = t.get("won", False)
                    break

            round_score = ""
            if len(teams) >= 2:
                scores = sorted(teams, key=lambda t: t.get("rounds", 0), reverse=True)
                round_score = f"{scores[0].get('rounds', 0)}-{scores[1].get('rounds', 0)}"

            processed.append({
                "map":         map_name,
                "agent":       agent,
                "kills":       kills,
                "deaths":      deaths,
                "assists":     assists,
                "won":         won,
                "round_score": round_score,
                "kd":          round(kills / max(deaths, 1), 2),
            })

        except Exception as e:
            print(f"Error processing match: {e}")
            continue

    return processed
