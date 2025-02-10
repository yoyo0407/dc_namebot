import os
import discord
from discord import app_commands
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
            width += 1
    return width

# 載入 .env
load_dotenv()

# 設定 intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="%", intents=intents)
tree = bot.tree  # 使用 app_commands 的指令管理

@bot.event
async def on_ready():
    await bot.tree.sync()  # ✅ 確保全伺服器同步指令
    print(f'✅ 已同步 {len(bot.tree.get_commands())} 個指令，全伺服器 & 私訊可用！')
    print(f'✅ Logged in as {bot.user}')


@tree.command(name="rks", description="計算 Rank Score")
async def rks(interaction: discord.Interaction, game: str, level: float, score: float):
    game = game.lower()
    rks = 0
    score_str = f"{score:.0f}"
    
    if game == "chu":
        thresholds = [
            (1009000, level + 2.15), (1007500, level + 2.0), (1005000, level + 1.5),
            (1000000, level + 1.0), (990000, level + 0.6), (975000, level),
            (925000, level - 3.0), (900000, level - 5.0), (800000, (level - 5.0) / 2)
        ]
        for i in range(len(thresholds) - 1):
            if thresholds[i + 1][0] <= score < thresholds[i][0]:
                x0, y0 = thresholds[i]
                x1, y1 = thresholds[i + 1]
                rks = y1 + (y0 - y1) * (score - x1) / (x0 - x1)
                break
        if score < 800000:
            rks = 0
    
    elif game == "phi":
        score_str = f"{score:.2f}"
        rks = 0 if score < 0.7 else ((score - 55) / 45) ** 2 * level
    
    elif game == "arc":
        thresholds = [
            (10000000, level + 2.00), (9950000, level + 1.75), (9900000, level + 1.50),
            (9800000, level + 1.00), (9500000, level), (9200000, level - 1.00),
            (8900000, level - 2.00), (8600000, level - 3.00)
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
        await interaction.response.send_message("❌ 遊戲名稱錯誤，請輸入 chu, phi, arc 或 t3")
        return
    
    await interaction.response.send_message(f"📊 遊戲：{game.upper()}\n🎚 等級：{level}\n🏆 分數：{score_str}\n🔢 Rank Score：{rks:.3f}")

@bot.tree.command(name="god", description="熊貓人舉牌")
@commands.is_owner()
async def god(interaction: discord.Interaction, *, name: str):
    print(f"🛠️ 指令觸發：{name}")
    
    # 計算文字長度
    text_length = get_text_width(name)
    
    img = Image.open("base.png")
    img = img.rotate(5, expand=True)
    draw = ImageDraw.Draw(img)
    
    # 計算文字大小
    text_size = min(230, 690 / text_length)
    
    # 字型 (請確保 `msjhbd.ttf` 存在)
    font_path = "msjhbd.ttf"
    try:
        font = ImageFont.truetype(font_path, text_size)
    except IOError:
        await interaction.response.send_message("❌ 找不到字型檔案！請確認 `msjhbd.ttf` 存在。")
        return

    # 計算文字範圍
    bbox = draw.textbbox((0, 0), name, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # 讓文字置中
    x = (1040 - text_width) // 2
    y = (360 - text_height) // 2

    draw.text((x, y), name, fill="black", font=font)
    
    # 旋轉、縮放圖片
    img = img.rotate(-5)
    img = img.resize((96, 96))
    
    # 儲存圖片
    img_path = "nameplate.png"
    img.save(img_path)

    # 回傳圖片
    await interaction.response.send_message(file=discord.File(img_path))

@tree.command(name="豆森pt", description="計算豆森PT")
async def dou(ctx: discord.Interaction, cp: int, bonus: int):
    x = 10 + int(cp / 45000)
    y = 100 + bonus
    base = int(x * y / 1000)*10
    await ctx.response.send_message(f"你的豆森PT(一小格黃體)為：{base * 5}\n你的豆森PT(一小格藍體)為：{base}")

# 確保 Token 被正確讀取
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    print("❌ 錯誤：未讀取到 Token，請檢查 .env 設定！")
    exit(1)

bot.run(TOKEN)