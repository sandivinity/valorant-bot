"""
utils/database.py — SQLite database layer for the leaderboard.

WHY SQLite OVER JSON?
JSON file problems:
  - If two people use /leaderboard-add at the same time, one write can corrupt the file
  - No way to query — you load the whole file every time
  - Not a real database — just a string

SQLite advantages:
  - Real database with tables, rows, and columns
  - Handles concurrent writes safely
  - You can query specific rows instead of loading everything
  - Industry standard — same concepts as PostgreSQL/MySQL (just simpler)
  - Zero setup — comes built into Python, no install needed

HOW IT WORKS:
We have one table called `leaderboard` with these columns:
  - server_id    : which Discord server this entry belongs to
  - user_id      : which Discord user registered
  - discord_name : their Discord username (for display)
  - val_name     : Valorant name e.g. "mofe"
  - val_tag      : Valorant tag e.g. "000"

SQL BASICS (you'll use these forever):
  CREATE TABLE — makes a new table (like creating a spreadsheet)
  INSERT OR REPLACE — adds a row, or updates it if it already exists
  SELECT — reads rows from a table
  DELETE — removes a row
  WHERE — filters which rows you want
"""

import aiosqlite  # async version of sqlite3 — works with discord.py's async pattern
import os

DB_PATH = "data/leaderboard.db"


async def init_db():
    """
    Creates the database file and table if they don't exist yet.
    Call this once on bot startup.
    
    IF NOT EXISTS means it's safe to call every time —
    it won't wipe your data if the table already exists.
    """
    os.makedirs("data", exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                server_id    TEXT NOT NULL,
                user_id      TEXT NOT NULL,
                discord_name TEXT,
                val_name     TEXT NOT NULL,
                val_tag      TEXT NOT NULL,
                PRIMARY KEY (server_id, user_id)
            )
        """)
        # PRIMARY KEY (server_id, user_id) means the combo of both must be unique
        # One Discord user can only have one entry per server
        await db.commit()
    print("✅ Database initialized")


async def add_player(server_id: str, user_id: str, discord_name: str, val_name: str, val_tag: str):
    """
    Adds or updates a player in the leaderboard.
    INSERT OR REPLACE handles both new entries and updates automatically.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR REPLACE INTO leaderboard
                (server_id, user_id, discord_name, val_name, val_tag)
            VALUES (?, ?, ?, ?, ?)
        """, (server_id, user_id, discord_name, val_name, val_tag))
        # The ? marks are placeholders — never put variables directly in SQL strings
        # That's called "SQL injection" and it's a security vulnerability
        await db.commit()


async def get_players(server_id: str) -> list[dict]:
    """
    Returns all registered players for a given server.
    SELECT * means "get all columns".
    WHERE filters to only this server's rows.
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row  # makes rows act like dicts
        async with db.execute("""
            SELECT * FROM leaderboard WHERE server_id = ?
        """, (server_id,)) as cursor:
            rows = await cursor.fetchall()
            # Convert Row objects to plain dicts for easier use
            return [dict(row) for row in rows]


async def remove_player(server_id: str, user_id: str):
    """Removes a player from the leaderboard."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            DELETE FROM leaderboard WHERE server_id = ? AND user_id = ?
        """, (server_id, user_id))
        await db.commit()
