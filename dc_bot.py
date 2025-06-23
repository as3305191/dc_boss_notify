import os
import sys
import discord
from discord.ext import commands
from flask import Flask, request
import threading

# 環境變數
TOKEN = os.getenv("DISCORD_TOKEN").strip()
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))
print(f"DISCORD_TOKEN: {TOKEN}")
print(f"TARGET_CHANNEL_ID: {TARGET_CHANNEL_ID}")

if not TOKEN or not TARGET_CHANNEL_ID:
    print("❌ 請設定 DISCORD_TOKEN 和 TARGET_CHANNEL_ID")
    sys.exit(1)

# 設定 Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask App
app = Flask(__name__)

@app.route("/api/send", methods=["POST"])
def send():
    msg = request.form.get("msg") or request.json.get("msg")
    if not msg:
        return {"error": "缺少參數 msg"}, 400

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel:
        bot.loop.create_task(channel.send(f"📢 來自遠端訊息：{msg}"))
        return {"ok": True, "sent": msg}
    else:
        return {"error": "找不到頻道"}, 500

# 啟動 Flask 伺服器
def run_flask():
    app.run(host="0.0.0.0", port=10000)  # Render 建議使用 PORT=10000 以上

# 啟動 Discord bot
@bot.event
async def on_ready():
    print(f"✅ Bot 已上線：{bot.user}")
    threading.Thread(target=run_flask).start()

bot.run(TOKEN)
