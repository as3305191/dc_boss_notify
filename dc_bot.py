import os
import sys
import io
import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import asyncio

# ... 你的 TOKEN, TARGET_CHANNEL_ID 驗證程式碼 ...

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

app = Flask(__name__)

@app.route("/api/send", methods=["POST"])
def send():
    msg = request.form.get("msg", "")

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "缺少圖片檔案參數 file"}), 400

    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if not channel:
        return jsonify({"error": "找不到頻道"}), 500

    image_data = file.read()
    file_stream = io.BytesIO(image_data)
    discord_file = discord.File(fp=file_stream, filename=file.filename)

    async def send_image():
        await channel.send(content=f"📷 來自遠端圖片訊息：{msg}" if msg else None, file=discord_file)

    future = asyncio.run_coroutine_threadsafe(send_image(), bot.loop)
    try:
        future.result(timeout=5)
        return jsonify({"ok": True, "filename": file.filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/ping", methods=["GET"])
def ping():
    return {"status": "alive"}

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f"🚀 Flask server running on port {port}")
    app.run(host="0.0.0.0", port=port)

@bot.event
async def on_ready():
    print(f"✅ Bot 已上線：{bot.user}")
    threading.Thread(target=run_flask).start()

bot.run(TOKEN)
