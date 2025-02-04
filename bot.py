import os
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv
import unicodedata

def get_text_width(text: str) -> int:
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ["W", "F"]:
            width += 1.5
        else:
            width += 1  # 英文算 1 格
    return width

# 載入 .env
load_dotenv() 

# 設定 intents，確保可以讀取訊息
intents = discord.Intents.default()
intents.message_content = True  # 允許讀取訊息
bot = commands.Bot(command_prefix="%", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

@bot.event
async def on_message(message):
    print(f"📩 收到訊息：{message.content}")  # 確保機器人有收到訊息
    await bot.process_commands(message)  # 讓指令繼續運行

@bot.command()
async def god(ctx, *, text: str):
    print(f"🛠️ 指令觸發：{text}")
    text_length = get_text_width(text)
    img = Image.open("base.png")
    img = img.rotate(5, expand=True)
    draw = ImageDraw.Draw(img)
    text_size = min(230, 690 / text_length)  # 計算文字大小
    # 字型 (請確保 `msjhbd.ttf` 存在)
    font_path = "msjhbd.ttf"
    try:
        font = ImageFont.truetype(font_path, text_size)
    except IOError:
        await ctx.send("❌ 找不到字型檔案！請確認 `msjhbd.ttf` 存在。")
        return

    # ✅ 計算文字大小
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 讓文字置中
    x = (1040 - text_width) // 2
    y = (360 - text_height) // 2

    draw.text((x, y), text, fill="black", font=font)
    img = img.rotate(-5)
    img = img.resize((96, 96))
    img_path = "nameplate.png"
    img.save(img_path)

    await ctx.send(file=discord.File(img_path))

# 確保 Token 被正確讀取
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    print("❌ 錯誤：未讀取到 Token，請檢查 .env 設定！")
    exit(1)

bot.run(TOKEN)
