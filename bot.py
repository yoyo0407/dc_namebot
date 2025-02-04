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
async def rks(ctx, game: str, level: float, score: float):
    game = game.lower()  # 轉換成小寫，避免大小寫影響
    rks = 0  # 預設 Rank Score
    score_str =f"{score:.0f}"
    if game == "chu":
        thresholds = [
            (1009000, level + 2.15),
            (1007500, level + 2.0),
            (1005000, level + 1.5),
            (1000000, level + 1.0),
            (990000, level + 0.6),
            (975000, level),
            (925000, level - 3.0),
            (900000, level - 5.0),
            (800000, (level - 5.0) / 2),
        ]
        for i in range(len(thresholds) - 1):
            if thresholds[i + 1][0] <= score < thresholds[i][0]:
                # 線性內插
                x0, y0 = thresholds[i]
                x1, y1 = thresholds[i + 1]
                rks = y1 + (y0 - y1) * (score - x1) / (x0 - x1)
                break
        if score < 800000:
            rks = 0

    elif game == "phi":
        score_str =f"{score:.2f}"
        bestAcc = score
        if bestAcc < 0.7:
            rks = 0
        else:
            rks = ((100 * bestAcc - 55) / 45) ** 2 * level

    elif game == "arc":
        thresholds = [
            (10000000, level + 2.00),
            (9950000, level + 1.75),
            (9900000, level + 1.50),
            (9800000, level + 1.00),
            (9500000, level),
            (9200000, level - 1.00),
            (8900000, level - 2.00),
            (8600000, level - 3.00),
        ]
        for i in range(len(thresholds) - 1):
            if thresholds[i + 1][0] <= score < thresholds[i][0]:
                x0, y0 = thresholds[i]
                x1, y1 = thresholds[i + 1]
                rks = y1 + (y0 - y1) * (score - x1) / (x0 - x1)
                break
        if score < 8600000:
            rks = 0

    elif game == "t3":
        if score < 800000:
            rks = 0
        elif score < 970000:
            rks = (level * (score - 800000) / 170000) / 34 * 40
        elif score < 990000:
            rks = (level + (score - 970000) / 20000) / 34 * 40
        elif score < 995000:
            rks = (level + 1 + (score - 990000) / 10000) / 34 * 40
        elif score < 999000:
            rks = (level + 1.5 + (score - 995000) / 8000) / 34 * 40
        else:
            rks = (level + 2 + (score - 999000) / 10000) / 34 * 40

    else:
        await ctx.send("❌ 遊戲名稱錯誤，請輸入 chu, phi, arc 或 t3")
        return

    await ctx.send(f"📊 遊戲：{game.upper()}\n🎚 等級：{level}\n🏆 分數：{score_str}\n🔢 Rank Score：{rks:.3f}")


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
