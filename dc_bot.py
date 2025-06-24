import os
import io
import sys
import discord
from discord.ext import commands
from flask import Flask, request ,jsonify
import threading

# 環境變數
TOKEN = os.getenv("DISCORD_TOKEN", "").strip()
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID", "").strip()

# 顯示安全資訊
print(f"DISCORD_TOKEN length: {len(TOKEN)}")
print(f"TARGET_CHANNEL_ID: {TARGET_CHANNEL_ID}")

# 驗證設定
if not TOKEN or not TARGET_CHANNEL_ID:
    print("❌ 請設定 DISCORD_TOKEN 和 TARGET_CHANNEL_ID")
    sys.exit(1)

try:
    TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)
except ValueError:
    print("❌ TARGET_CHANNEL_ID 必須是整數")
    sys.exit(1)

# 設定 Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Flask App
app = Flask(__name__)


@app.route("/api/send", methods=["POST"])
def send():
    # 接收文字訊息（可選）
    msg = request.form.get("msg", "")

    # 接收檔案
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "缺少圖片檔案參數 file"}), 400

    # 確認 Discord 頻道
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        return jsonify({"error": "找不到頻道"}), 500

    # 將檔案轉為 discord.File 格式
    image_data = file.read()
    file_stream = io.BytesIO(image_data)
    discord_file = discord.File(fp=file_stream, filename=file.filename)

    # 送出圖片（與可選訊息）
    async def send_image():
        await channel.send(content=f"📷 來自遠端圖片訊息：{msg}" if msg else None, file=discord_file)

    # 使用 run_coroutine_threadsafe 更穩定
    import asyncio
    future = asyncio.run_coroutine_threadsafe(send_image(), bot.loop)
    try:
        future.result(timeout=5)
        return jsonify({"ok": True, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ping", methods=["GET"])
def ping():
    return {"status": "alive"}

# 啟動 Flask 伺服器
def run_flask():
    port = int(os.environ.get("PORT", 10000))  # Render 指定的 port
    print(f"🚀 Flask server running on port {port}")
    app.run(host="0.0.0.0", port=port)

# 啟動 Discord bot
@bot.event
async def on_ready():
    print(f"✅ Bot 已上線：{bot.user}")
    threading.Thread(target=run_flask).start()

bot.run(TOKEN)
