# Firebase Setup Guide for CTF Time Bot

## ✅ Migration Complete!

Your bot has been successfully migrated from JSON file storage to Firebase Realtime Database. All guild configurations will now persist across restarts and redeployments on Render.

## 🔥 Firebase Project Setup

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or **"Create a project"**
3. Enter project name (e.g., `ctf-time-bot`)
4. Disable Google Analytics (not needed for this project)
5. Click **"Create project"**

### Step 2: Enable Realtime Database

1. In the Firebase Console, click on **"Build"** → **"Realtime Database"**
2. Click **"Create Database"**
3. Choose location closest to you (e.g., `us-central1` or `europe-west1`)
4. Select **"Start in test mode"** for now (we'll secure it in Step 3)
5. Click **"Enable"**

### Step 3: Configure Security Rules

⚠️ **IMPORTANT**: Test mode allows anyone to read/write. Update security rules:

1. In Realtime Database, go to the **"Rules"** tab
2. Replace the rules with:

```json
{
  "rules": {
    ".read": false,
    ".write": false
  }
}
```

3. Click **"Publish"**

This locks down the database to only service account access (your bot).

### Step 4: Generate Service Account Credentials

1. In Firebase Console, click the **⚙️ gear icon** → **"Project settings"**
2. Go to **"Service accounts"** tab
3. Click **"Generate new private key"**
4. Click **"Generate key"** in the confirmation dialog
5. A JSON file will be downloaded (e.g., `ctf-time-bot-firebase-adminsdk-xxxxx.json`)
6. **⚠️ KEEP THIS FILE SECRET!** Never commit it to Git

### Step 5: Get Database URL

1. In Realtime Database page, look at the top
2. Copy the database URL (looks like: `https://ctf-time-bot-default-rtdb.europe-west1.firebasedatabase.app/`)
3. Save this URL, you'll need it for configuration

## 🖥️ Local Development Setup

### Step 1: Add Credentials to Project

1. Place the downloaded JSON file in your project root (e.g., `firebase-credentials.json`)
2. It's already excluded from Git by `.gitignore`

### Step 2: Update .env File

Add these two environment variables to your `.env` file:

```env
DISCORD_TOKEN=your_existing_discord_token

# Firebase Configuration
FIREBASE_DATABASE_URL=https://your-project-id-default-rtdb.firebaseio.com/
FIREBASE_CREDENTIALS=firebase-credentials.json
```

Replace:
- `https://your-project-id-default-rtdb.firebaseio.com/` with YOUR database URL from Step 5 above
- `firebase-credentials.json` with the path to your JSON file

### Step 3: Test Locally

1. Install Firebase dependencies:
   ```powershell
   pip install firebase-admin
   ```

2. Run the bot:
   ```powershell
   python main.py
   ```

3. Check for the Firebase connection message:
   ```
   Bot is running!
   ✅ Firebase connected successfully
   ```

4. Test with `/set_schedule_channel` command in your Discord server

## ☁️ Render Deployment

### Step 1: Prepare Credentials for Render

Since we can't upload files directly to Render, we'll store the entire JSON as an environment variable:

1. Open your `firebase-credentials.json` file in a text editor
2. Copy the ENTIRE contents (it's one JSON object)
3. You'll paste this in Render

### Step 2: Configure Render Environment Variables

1. Go to your Render dashboard
2. Select your web service
3. Go to **"Environment"** tab
4. Add these environment variables:

| Key | Value | Notes |
|-----|-------|-------|
| `DISCORD_TOKEN` | Your bot token | Same as before |
| `FIREBASE_DATABASE_URL` | `https://your-project-id-default-rtdb.firebaseio.com/` | From Firebase console |
| `FIREBASE_CREDENTIALS` | Paste entire JSON contents | The full JSON object from credentials file |

**For FIREBASE_CREDENTIALS:**
- Click "Add Environment Variable"
- Key: `FIREBASE_CREDENTIALS`
- Value: Paste the ENTIRE JSON contents (including all curly braces `{}`)
- Example format:
  ```json
  {
    "type": "service_account",
    "project_id": "your-project",
    "private_key_id": "...",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-...@your-project.iam.gserviceaccount.com",
    ...
  }
  ```

4. Click **"Save Changes"**

### Step 3: Deploy

1. Push your code to GitHub (the credentials are gitignored, so they won't be pushed)
2. Render will automatically redeploy
3. Check the logs for:
   ```
   Bot is running!
   ✅ Firebase connected successfully
   [AUTO-SCHEDULER] Starting scheduling task for guild XXXXX
   ```

## 🔄 Migrating Existing Configurations

If you have an existing `schedule_multi.json` file with guild configurations:

### Option 1: Manual Migration (Recommended)

1. Use Discord commands to reconfigure each server:
   ```
   /set_schedule_channel #your-channel
   /set_schedule_time 9 0
   /set_timezone Europe/Rome
   ```

2. Delete the old `schedule_multi.json` file

### Option 2: Import Script (Advanced)

If you have many servers configured, you can import from JSON:

```python
import json
import firebase_db

# Initialize Firebase
firebase_db.init_firebase()

# Load old config
with open('schedule_multi.json', 'r') as f:
    old_configs = json.load(f)

# Import to Firebase
for guild_id, config in old_configs.items():
    firebase_db.save_guild_config(guild_id, config)
    print(f"✅ Migrated config for guild {guild_id}")

print("Migration complete!")
```

Run this once locally, then delete `schedule_multi.json`.

## ✅ Verification Checklist

After deployment, verify everything works:

- [ ] Bot comes online in Discord
- [ ] Firebase connection message appears in logs
- [ ] `/set_schedule_channel` command works
- [ ] `/schedule_status` shows your configuration
- [ ] Configuration persists after bot restart
- [ ] Scheduler starts automatically on bot startup
- [ ] Daily messages are sent at configured time

## 🐛 Troubleshooting

### Error: "Failed to initialize Firebase"

**Cause:** Invalid credentials or database URL

**Solution:**
1. Check `FIREBASE_DATABASE_URL` is correct (no trailing slash)
2. Verify `FIREBASE_CREDENTIALS` contains valid JSON
3. Ensure the JSON includes `private_key` field with actual key
4. Check Render logs for specific error message

### Error: "Permission Denied"

**Cause:** Database security rules are too restrictive

**Solution:**
1. Go to Firebase Console → Realtime Database → Rules
2. Verify rules are:
   ```json
   {
     "rules": {
       ".read": false,
       ".write": false
     }
   }
   ```
3. If you used different rules, the service account needs access

### Configuration Not Persisting

**Cause:** Firebase writes are failing silently

**Solution:**
1. Check Render logs for Firebase errors
2. Verify environment variables are set correctly
3. Test locally first to isolate the issue

### Bot Restarts But Scheduler Doesn't Start

**Cause:** Configuration exists but scheduler task isn't created

**Solution:**
1. Check if `channel_id` is set in Firebase
2. Look for `[AUTO-SCHEDULER]` messages in logs
3. Use `/restart_scheduler` command to manually restart

## 📊 Firebase Data Structure

Your data in Firebase looks like this:

```
root/
├── guild_123456789/
│   ├── channel_id: 987654321
│   ├── hour: 9
│   ├── minute: 0
│   └── timezone: "Europe/Rome"
├── guild_111222333/
│   ├── channel_id: 444555666
│   ├── hour: 10
│   ├── minute: 30
│   └── timezone: "America/New_York"
└── ...
```

You can view and edit this data directly in the Firebase Console under "Realtime Database" → "Data" tab.

## 💰 Firebase Pricing

**Good news:** The free tier is generous!

**Firebase Realtime Database Free Tier:**
- 1 GB storage (you'll use ~1 KB per server)
- 10 GB/month bandwidth
- 100 simultaneous connections

**Your usage:** ~1 KB total for all servers combined

You're well within free tier limits! 🎉

## 🎯 Next Steps

1. ✅ Complete Firebase setup (Steps 1-4 above)
2. ✅ Test locally with your credentials
3. ✅ Deploy to Render with environment variables
4. ✅ Configure UptimeRobot to ping your bot every 5 minutes
5. ✅ Enjoy 24/7 hosting with persistent configuration!

## 🆘 Need Help?

- **Firebase Documentation:** https://firebase.google.com/docs/database
- **Render Documentation:** https://render.com/docs
- **Check Render Logs:** Dashboard → Your Service → Logs tab

---

**Congratulations!** Your bot now has production-grade persistent storage! 🚀
