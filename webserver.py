from flask import Flask
from threading import Thread
import os

app = Flask('')

@app.route('/')
def home():
    return "Discord CTF Bot is running! ✅"

@app.route('/health')
def health():
    return {"status": "ok", "message": "Bot is alive"}, 200

def run():
    # Use the PORT environment variable provided by Render, fallback to 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()