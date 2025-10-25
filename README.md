
# 🕛 CTFTimeBot (Notifier)

**[➕ Add to Discord](https://top.gg/bot/1217196592046538993) | [⭐ Vote on TOP.GG](https://top.gg/bot/1217196592046538993)**

An advanced and reliable Discord bot that automatically posts upcoming Capture The Flag (CTF) events from CTFtime.org to your server.

Stay organized, never miss a competition, and keep your CTF team informed automatically!

## **Note about the name and relationship with CTFTime**

CTFTime is an independent website. This project is not affiliated with the CTFTime development team and does not intend to replace them. The name "CTFTimeBot" was chosen solely to make the bot's purpose immediately clear: the bot uses publicly available data on CTFtime.org by performing HTTP (GET) requests to the "upcoming events" page to retrieve events. For official information, updates, or issues related to the listed data, consult CTFtime.org or contact their team directly. This project does not in any way represent CTFtime.org. Profile images and any other multimedia content used come from their respective public sources; the copyright for such content is and remains assigned to the rightful owners, and this project does not claim ownership.

## 🆕 **Recent Major Changes (2025)**

- **🔥 Firebase Realtime Database Integration**: Complete migration from local JSON files to cloud-based persistent storage
- **☁️ Persistent Configuration**: All settings survive bot restarts, crashes, and redeployments automatically
- **Multi-server support**: Each server (guild) has its own independent scheduling and configuration
- **Robust scheduler management**: The scheduler task is now tracked per-guild with a global registry, ensuring reliable status and restart
- **Automatic scheduler restart**: Any change to schedule channel, time, or timezone immediately cancels and restarts the scheduler for that server
- **Auto-recovery on restart**: Bot automatically restores all server configurations and schedulers from Firebase on startup
- **Scheduler status and logs**: `/scheduler_logs` and `/debug` now show accurate, real-time information about the scheduler and configuration for each server
- **Help command cleaned up**: `/help_ctf` now only lists working and available commands
- **Advanced debug tools**: Improved `/debug` output, including config, permissions, and script checks
- **Safer task handling**: The bot prevents duplicate or zombie scheduler tasks and always reflects the latest config
- **Improved error handling**: More robust feedback and error messages for all commands
- **Cleaner code and documentation**: All commands and help texts are up-to-date and reflect the real bot capabilities
- **24/7 hosting ready**: Optimized for Render.com with automatic keep-alive and environment variable support

---


## 🚀 Main Features


* ⏰ **Automatic Daily Updates**  
  The bot fetches and posts a list of upcoming CTF events every day at your preferred time.
* 🔥 **Firebase Cloud Storage**  
  All configurations are stored in Firebase Realtime Database - survive restarts, crashes, and redeployments automatically.
* ☁️ **Zero Data Loss**  
  Your settings persist forever in the cloud, no local file dependencies.
* 🌍 **Complete Timezone Support**  
  Configurable for any timezone worldwide (Europe/Rome, America/New_York, Asia/Tokyo, etc.).
* 🕐 **Customizable Schedule Time**  
  Set your preferred time for daily messages (not just midnight!).
* 🗑️ **Automatic Channel Cleanup**  
  Automatically clears previous messages before sending updates.
* 📅 **CTF Events at a Glance**  
  Displays event name, date, duration, and direct link for each upcoming competition.
* 🔧 **Advanced Debug Tools**  
  Complete monitoring and diagnostic system for administrators.
* 🌐 **Data from CTFtime.org**  
  Always up to date using official data directly from the CTFtime website.
* 🏢 **Multi-server aware**  
  Each Discord server has its own independent configuration and scheduler.
* 🔄 **Automatic scheduler restart**  
  Any change to channel, time, or timezone restarts the scheduler for that server.
* 🔁 **Auto-recovery**  
  Bot automatically restores all configurations and restarts all schedulers after any restart.
* 🛡️ **Reliable scheduler status/logs**  
  `/scheduler_logs` and `/debug` always reflect the real state of the scheduler and config.
* 🧹 **Clean and up-to-date help**  
  `/help_ctf` only shows working commands.


## 📋 Available Commands (2025)

### 📢 Main Commands

| Command | Description |
|---------|-------------|
| `/upcoming` | Immediately shows upcoming CTF events |
| `/upcoming_events` | Alias for `/upcoming` |
| `/help_ctf` | Shows all available commands |

### ⚙️ Scheduling Configuration

| Command | Description |
|---------|-------------|
| `/set_schedule_channel` | Sets current channel for daily messages (restarts scheduler) |
| `/unset_schedule_channel` | Removes scheduled channel (stops scheduler) |
| `/schedule_status` | Shows current scheduler status |

### 🕐 Time Management

| Command | Example | Description |
|---------|---------|-------------|
| `/set_schedule_time <hour> [minute]` | `/set_schedule_time 8 30` | Sets time for messages (restarts scheduler) |
| `/get_schedule_time` | - | Shows currently set time |
| `/reset_schedule_time` | - | Resets time to midnight (restarts scheduler) |

### 🌍 Timezone Management

| Command | Example | Description |
|---------|---------|-------------|
| `/set_timezone <timezone>` | `/set_timezone Europe/Rome` | Sets timezone (restarts scheduler) |
| `/get_timezone` | - | Shows currently set timezone |
| `/list_timezones [region]` | `/list_timezones Europe` | Lists available timezones |
| `/reset_timezone` | - | Resets to Europe/Rome (restarts scheduler) |

### 🔧 Administrator Commands

> ⚠️ **Note:** These commands require administrator permissions

| Command | Description |
|---------|-------------|
| `/test_schedule` | Tests scheduled sending (with channel cleanup) |
| `/force_schedule` | Forces immediate sending of scheduled message |
| `/test_now` | Quick test without message deletion |
| `/clear_channel` | Clears all messages from scheduled channel |
| `/debug` | Shows detailed debug information (per-server) |
| `/scheduler_logs` | Checks scheduling task status (per-server, always accurate) |
| `/restart_scheduler` | Restarts scheduling task for this server |


## 🎯 Quick Start Guide (Multi-server, 2025)

### 1️⃣ Initial Setup
```
1. /set_schedule_channel          # In the channel where you want messages (restarts scheduler)
2. /set_schedule_time 8 0         # Set time (e.g., 08:00, restarts scheduler)
3. /set_timezone Europe/Rome      # Set your timezone (restarts scheduler)
```

### 2️⃣ Verify Configuration
```
/schedule_status                  # Check that everything is configured
```

### 3️⃣ Test Functionality
```
/test_now                        # Quick test
/force_schedule                  # Complete test with cleanup
```

## 🌍 Supported Timezones

The bot supports all standard timezones. Some examples:

**Europe:**
- `Europe/Rome` (Italy)
- `Europe/London` (United Kingdom)
- `Europe/Paris` (France)
- `Europe/Berlin` (Germany)

**America:**
- `America/New_York` (USA East)
- `America/Los_Angeles` (USA West)
- `America/Chicago` (USA Central)
- `America/Toronto` (Canada)

**Asia:**
- `Asia/Tokyo` (Japan)
- `Asia/Shanghai` (China)
- `Asia/Mumbai` (India)
- `Asia/Dubai` (UAE)

**Oceania:**
- `Australia/Sydney`
- `Pacific/Auckland`

Use `/list_timezones` to see all available timezones or `/list_timezones [region]` for a specific region.


## ➕ Add the Bot to Your Server

**[🎯 Invite CTFTime Notifier Bot from TOP.GG](https://top.gg/bot/1217196592046538993)**

The bot is hosted 24/7 and ready to use! Simply click the link above to add it to your Discord server.

### 🚀 Quick Start

Once invited to your server:

1. **Set your channel**: Run `/set_schedule_channel` in the channel where you want daily updates
2. **Customize (optional)**:
   - `/set_schedule_time 9 0` - Set time (e.g., 09:00)
   - `/set_timezone Europe/Rome` - Set your timezone
3. Done! The bot will automatically post CTF events daily 🎉

### 🔐 Required Bot Permissions

Make sure the bot has these permissions:
- ✅ **Send Messages** - To post updates
- ✅ **Manage Messages** - To clear old messages
- ✅ **Embed Links** - To show formatted event cards


## 🛠️ Troubleshooting

### 📋 Prerequisites

1. **Discord Bot Token**: Create a bot at [Discord Developer Portal](https://discord.com/developers/applications)
2. **Firebase Project**: Set up Firebase Realtime Database (see [FIREBASE_SETUP.md](FIREBASE_SETUP.md))
3. **Hosting Platform**: Recommended: [Render.com](https://render.com) (free tier available)

### ☁️ Deploy on Render (Recommended - Free 24/7 Hosting)

#### 1. Fork/Clone this Repository

```bash
git clone https://github.com/Mrk756/CtfTimeBot.git
cd CtfTimeBot
```

#### 2. Set up Firebase

Follow the complete guide in [FIREBASE_SETUP.md](FIREBASE_SETUP.md) to:
- Create a Firebase project
- Enable Realtime Database
- Download service account credentials
- Get your database URL

#### 3. Deploy to Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `ctftime-bot` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: (leave empty, auto-detected from `requirements.txt`)
   - **Start Command**: (auto-detected from `Procfile`: `python main.py`)
   - **Plan**: Free

#### 4. Add Environment Variables

In Render, go to **Environment** tab and add:

| Variable | Value | Where to Find |
|----------|-------|---------------|
| `DISCORD_TOKEN` | Your Discord bot token | [Discord Developer Portal](https://discord.com/developers/applications) |
| `FIREBASE_DATABASE_URL` | `https://your-project.firebaseio.com/` | Firebase Console → Realtime Database |
| `FIREBASE_CREDENTIALS` | Entire JSON from credentials file | Downloaded from Firebase (paste full JSON) |

**Important**: For `FIREBASE_CREDENTIALS`, paste the **entire content** of your Firebase credentials JSON file.

#### 5. Deploy!

Click **"Create Web Service"** - Render will automatically:
- Install dependencies from `requirements.txt`
- Start the bot with the `Procfile`
- Keep it running 24/7

### 🖥️ Local Development

#### 1. Clone and Install

```bash
git clone https://github.com/Mrk756/CtfTimeBot.git
cd CtfTimeBot
pip install -r requirements.txt
```

#### 2. Configure Environment

Create a `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

Place your Firebase credentials JSON file as `firebase-credentials.json` in the project root.

#### 3. Run

```bash
python main.py
```

### 🔧 Keep Bot Alive 24/7 (Optional but Recommended)

Render free tier sleeps after 15 minutes of inactivity. Use [UptimeRobot](https://uptimerobot.com/) (free) to ping your bot every 5 minutes:

1. Sign up at [UptimeRobot](https://uptimerobot.com/)
2. Create a new monitor:
   - **Monitor Type**: HTTP(s)
   - **URL**: Your Render URL (e.g., `https://ctftime-bot.onrender.com`)
   - **Monitoring Interval**: 5 minutes
3. Save - your bot will never sleep! 🎉

### 📦 Dependencies

```
python-dotenv    # Environment variables
nextcord        # Discord API wrapper
beautifulsoup4  # HTML parsing for CTFtime.org
requests        # HTTP requests
flask           # Keep-alive web server
firebase-admin  # Firebase Realtime Database
```

All automatically installed from `requirements.txt`.

### 🔐 Security Notes

- ✅ Never commit `.env` file or Firebase credentials to Git
- ✅ Use environment variables for all secrets
- ✅ Firebase credentials are in `.gitignore`
- ✅ Configure Firebase security rules (see [FIREBASE_SETUP.md](FIREBASE_SETUP.md))

## �🛠️ Troubleshooting (2025)

### Bot not sending scheduled messages?
1. Check with `/scheduler_logs` if the task is active (per-server, always up-to-date)
2. Verify configuration with `/debug` (per-server)
3. Try `/restart_scheduler` if necessary (reliable, per-server)

### Timezone errors?
1. Use `/list_timezones` to see valid timezones
2. Check current timezone with `/get_timezone`
3. Reset with `/reset_timezone` if necessary

### Permission issues?
The bot needs these permissions:
- ✅ Send Messages
- ✅ Manage Messages (for channel cleanup)
- ✅ Embed Links

### Firebase connection failed?
1. Check `FIREBASE_DATABASE_URL` is correct (no trailing `/` issues)
2. Verify `FIREBASE_CREDENTIALS` contains valid JSON
3. Ensure Firebase security rules allow service account access
4. Check Render logs for specific error messages

### Configuration not persisting after restart?
This should **never** happen with Firebase! The bot automatically restores all configurations when it comes back online.

If you experience issues:
- Use `/debug` to check your current configuration
- Try `/restart_scheduler` to manually restart the scheduler
- Contact support if the problem persists

## 📸 Example Output

![CTF Events Example](https://github.com/user-attachments/assets/a4d8c377-2357-473c-8e0d-e628755d4953)

## 🔄 Updates and Features

**2025 Major Updates:**
- Multi-server support with per-guild configuration and scheduling
- Global scheduler task registry for robust status and restart
- Automatic scheduler restart on every config change (channel, time, timezone)
- `/scheduler_logs` and `/debug` always reflect the real state
- `/help_ctf` cleaned up and always up-to-date
- Improved error handling and feedback
- No more zombie or duplicate scheduler tasks

---

## �‍💻 For Developers

Want to self-host or contribute to the bot? Here's what you need to know:

### 🛠️ Tech Stack

- **Language**: Python 3.13+
- **Discord Library**: [nextcord](https://github.com/nextcord/nextcord)
- **Database**: Firebase Realtime Database
- **Web Scraping**: BeautifulSoup4 + Requests
- **Hosting**: Render.com (or any Python hosting platform)
- **Keep-Alive**: Flask web server

### 📦 Installation & Setup

#### 1. Clone Repository

```bash
git clone https://github.com/Mrk756/CtfTimeBot.git
cd CtfTimeBot
pip install -r requirements.txt
```

#### 2. Firebase Setup

Follow the complete guide in **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** to:
- Create a Firebase project
- Enable Realtime Database
- Download service account credentials
- Configure security rules

#### 3. Environment Variables

Create a `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
```

Or for cloud deployment (e.g., Render):

```env
DISCORD_TOKEN=your_discord_bot_token
FIREBASE_DATABASE_URL=https://your-project-default-rtdb.firebaseio.com/
FIREBASE_CREDENTIALS=<paste entire Firebase credentials JSON>
```

#### 4. Run Locally

```bash
python main.py
```

### ☁️ Deploy to Render

1. Fork this repository
2. Create a new **Web Service** on [Render](https://render.com)
3. Connect your GitHub repository
4. Add environment variables (see step 3 above)
5. Deploy! The `Procfile` and `requirements.txt` handle the rest

**Render Configuration:**
- **Build Command**: (auto-detected from `requirements.txt`)
- **Start Command**: `python main.py` (from `Procfile`)
- **Environment**: Python 3

### 🔧 Project Structure

```
CtfTimeBot/
├── main.py                 # Main bot logic & commands
├── firebase_db.py          # Firebase database abstraction
├── webserver.py            # Flask keep-alive server
├── upcoming_events.py      # CTFtime.org scraper
├── requirements.txt        # Python dependencies
├── Procfile               # Render deployment config
├── .env                   # Environment variables (local)
├── .gitignore            # Git ignore rules
├── README.md             # This file
└── FIREBASE_SETUP.md     # Firebase setup guide
```

### 🔐 Security Notes

- ✅ Never commit `.env` or `firebase-credentials.json`
- ✅ Use environment variables for all secrets
- ✅ Configure Firebase security rules (see `FIREBASE_SETUP.md`)
- ✅ Keep dependencies updated

### 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

**Areas for contribution:**
- Bug fixes
- New features (e.g., more CTF platforms)
- Documentation improvements
- Code optimization

### 📚 Additional Developer Documentation

- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** - Complete Firebase setup guide
- **[requirements.txt](requirements.txt)** - Python dependencies
- **[Procfile](Procfile)** - Deployment configuration

### 📄 License

This project is open source and available under the MIT License.

---

## 💬 Support & Community

- **Need help?** Use `/help_ctf` in Discord
- **Bug reports**: [GitHub Issues](https://github.com/Mrk756/CtfTimeBot/issues)
- **Vote for the bot**: [TOP.GG](https://top.gg/bot/1217196592046538993) ⭐

## 🙏 Acknowledgments

- CTF events data from [CTFtime.org](https://ctftime.org/)
- Built with [nextcord](https://github.com/nextcord/nextcord)
- Persistent storage with [Firebase](https://firebase.google.com/)
- Hosted on [Render](https://render.com/)
- Available on [TOP.GG](https://top.gg/bot/1217196592046538993)

---

**Keep your CTF team always updated! 🚀**

**[➕ Add to Discord](https://top.gg/bot/1217196592046538993) | [⭐ Vote on TOP.GG](https://top.gg/bot/1217196592046538993) | [🐛 Report Issues](https://github.com/Mrk756/CtfTimeBot/issues)**

**Need help?** Check [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed setup instructions or open an issue on GitHub.




