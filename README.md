# 🎮 Valorant Stats Discord Bot

A Discord bot that lets players look up live Valorant stats, ranks, and match history using slash commands. Built with Python and discord.py, powered by the [Henrik Valorant API](https://docs.henrikdev.xyz/valorant).

---

## ✨ Features

| Command | Description |
|---|---|
| `/stats name tag` | Rank, RR, ELO, peak rank, and last 5 matches |
| `/leaderboard-add name tag` | Register your account to the server |
| `/leaderboard` | See your server's ranked leaderboard |
| `/help` | All available commands |

---

## 📸 Preview

<img width="657" height="660" alt="image" src="https://github.com/user-attachments/assets/d51ad2bf-5d2a-4ec6-8ba0-989aacdbf956" />


---

## 🛠 Tech Stack

- **Python 3.11+**
- **discord.py 2.3** — slash commands, embeds, Cog architecture
- **aiohttp** — async HTTP requests to the Valorant API
- **python-dotenv** — secure token management
- **Henrik's Valorant API** — unofficial but reliable Valorant data

---

## 🚀 Setup & Running Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/valorant-bot.git
cd valorant-bot
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your bot token
```bash
cp .env.example .env
```
Then open `.env` and replace `your_discord_bot_token_here` with your actual token.

### 5. Run the bot
```bash
python main.py
```

You should see:
```
✅ Logged in as YourBot#1234
✅ Synced 4 slash command(s)
✅ Loaded: commands.stats
✅ Loaded: commands.leaderboard
✅ Loaded: commands.help
```

---

## 🔑 Getting Your Discord Bot Token

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Click **New Application** → give it a name
3. Click **Bot** in the left sidebar → **Reset Token** → copy it
4. Under **Privileged Gateway Intents**, enable **Message Content Intent**
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Embed Links`, `Use Slash Commands`
6. Copy the generated URL → open it in your browser → add the bot to your server

---

## 📁 Project Structure

```
valorant-bot/
├── main.py                  # Bot startup, loads all Cogs
├── requirements.txt         # Python package list
├── .env.example             # Template for secrets (copy to .env)
├── .gitignore               # Prevents secrets from being pushed
│
├── commands/                # Each file = a group of related commands
│   ├── __init__.py
│   ├── stats.py             # /stats command
│   ├── leaderboard.py       # /leaderboard and /leaderboard-add
│   └── help.py              # /help command
│
├── utils/                   # Reusable helper modules
│   ├── __init__.py
│   ├── api.py               # All Valorant API calls (data layer)
│   └── embeds.py            # Discord embed builders (presentation layer)
│
└── data/                    # Auto-created at runtime
    └── leaderboard.json     # Per-server leaderboard storage
```

---

## 🧠 Key Concepts Used

- **Async/Await** — Non-blocking API calls so the bot never freezes
- **Discord Cogs** — Modular command architecture (like controllers in MVC)
- **Slash Commands** — Modern Discord UX with autocomplete and input validation
- **REST API Integration** — Fetching and parsing JSON from a 3rd-party API
- **Data Persistence** — JSON file storage for leaderboard data
- **Environment Variables** — Secure secret management with `.env`

---

## 📝 License

MIT — free to use, modify, and distribute.

---

> Built by [Your Name](https://github.com/YOUR_USERNAME) — 1st year Software Engineering student 🎓
=======
# valorant-bot
A Discord bot that lets players look up live Valorant stats, ranks, and match history using slash commands. Built with Python and discord.py.
>>>>>>> 19a31dff1b985dbda8b4ef589154a16a2b4c9a02
