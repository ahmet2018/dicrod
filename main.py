import discord
from discord.ext import commands
import random
import os
import requests
from enum import Enum
import asyncio
from flask import Flask
from threading import Thread
import io

# --- KART ÜRETİM MANTIĞI ---

class Card(Enum):
    Visa = 0
    Mastercard = 1

def computeCheckDigit(cardNumber):
    total = 0
    digits = cardNumber[::-1]
    for i in range(len(digits)):
        digit = int(digits[i])
        if i % 2 == 0:
            digit *= 2
        total += sum(map(int, str(digit)))
    return (total * 9) % 10

def fillToLength(text, length):
    toAdd = length - len(text)
    for _ in range(toAdd):
        text += str(random.randint(0, 9))
    return text

def genCardNumber(cardType):
    if cardType == Card.Visa:
        length = 16
        prefix = str(4)
    elif cardType == Card.Mastercard:
        length = 16
        prefix = str(random.randint(51, 55))
    else:
        raise Exception("Gecersiz kart tipi!")
    cardNumber = fillToLength(prefix, length - 1)
    return cardNumber + str(computeCheckDigit(cardNumber))

def generateCVV():
    return f"{random.randint(0,9)}{random.randint(0,9)}{random.randint(0,9)}"

def generateEXP():
    ay = random.randint(1, 12)
    yil = random.randint(26, 40)
    return f"{ay:02d}|20{yil}"

_bin_cache = {}
_session = requests.Session()
_session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})

async def get_bin_info_async(card_number):
    bin6 = card_number[:6]
    if bin6 in _bin_cache:
        return _bin_cache[bin6]

    try:
        url = f"https://binlist.io/lookup/{bin6}/"
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: _session.get(url, timeout=2)) # Timeout düşürüldü
        
        if resp.status_code == 200:
            data = resp.json()
            country = data.get("country", {})
            country_name = country.get("name", "UNKNOWN")
            bank = data.get("bank", {})
            bank_name = bank.get("name", "Unknown Bank")
            card_type = data.get("type", "UNKNOWN").upper()
            if card_type not in ["CREDIT", "DEBIT"]:
                card_type = "UNKNOWN"
            result = f"[{country_name}] {bank_name} ({card_type})"
        else:
            result = "[UNKNOWN] Unknown Bank (UNKNOWN)"
    except Exception:
        result = "[UNKNOWN] Unknown Bank (UNKNOWN)"

    _bin_cache[bin6] = result
    return result

# --- DISCORD BOT KURULUMU ---

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot aktif: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(name="!gen <visa/master> <adet>"))

@bot.command()
async def gen(ctx, card_type: str = None, count: int = 1):
    if card_type is None or card_type.lower() not in ["visa", "master"]:
        await ctx.send("❌ Lütfen geçerli bir kart tipi belirtin: `!gen visa 5` veya `!gen master 5`", delete_after=10)
        return

    # Limit 1 Milyon
    if count > 1000000:
        await ctx.send("⚠️ Tek seferde en fazla 1.000.000 kart üretebilirsiniz.", delete_after=10)
        count = 1000000
    
    if count < 1:
        count = 1

    try:
        await ctx.author.send(f"⏳ **{count:,}** adet **{card_type.upper()}** kart üretiliyor, lütfen bekleyin...")
        await ctx.send(f"✅ Talebiniz alındı {ctx.author.mention}, kartları DM kutunuza gönderiyorum!", delete_after=10)
    except discord.Forbidden:
        await ctx.send(f"❌ {ctx.author.mention}, DM kutun kapalı! Lütfen DM'lerini açıp tekrar dene.", delete_after=15)
        return

    card_type_enum = Card.Visa if card_type.lower() == "visa" else Card.Mastercard
    results_list = []
    
    # Reklam Metni
    header = "========================================\n"
    header += "MADE BY ZADREX\n"
    header += "Discord: https://discord.gg/ty2w9dUd3K\n"
    header += "========================================\n\n"
    
    footer = "\n========================================\n"
    footer += "MADE BY ZADREX\n"
    footer += "Discord: https://discord.gg/ty2w9dUd3K\n"
    footer += "========================================\n"

    # Hızlı Üretim Döngüsü
    for i in range(count):
        card_number = genCardNumber(card_type_enum)
        exp_date = generateEXP()
        cvv = generateCVV()
        
        # Eğer sayı çok fazlaysa BIN sorgusunu atla (Performans için)
        if count <= 100:
            bin_info = await get_bin_info_async(card_number)
            line = f"{card_number}|{exp_date}|{cvv} - {bin_info}"
        else:
            line = f"{card_number}|{exp_date}|{cvv}"
            
        results_list.append(line)
        
        # Her 10.000 kartta bir küçük bir nefes al (Botun donmaması için)
        if i % 10000 == 0 and i > 0:
            await asyncio.sleep(0.1)

    # TXT Dosyası Oluşturma
    file_content = header + "\n".join(results_list) + footer
    file_buffer = io.BytesIO(file_content.encode('utf-8'))
    discord_file = discord.File(fp=file_buffer, filename=f"zadrex_cards_{card_type}_{count}.txt")

    # DM Gönderimi
    embed = discord.Embed(title=f"✅ {card_type.upper()} Kartlar Üretildi", color=discord.Color.blue())
    
    if count <= 15:
        embed.description = f"```\n" + "\n".join(results_list) + "```"
    else:
        embed.description = f"**{count:,}** adet kart üretildi.\n\n**Made by zadrex**\nDiscord: https://discord.gg/ty2w9dUd3K"

    embed.set_footer(text="Zadrex CC Creator | 1M Limit")
    
    await ctx.author.send(embed=embed, file=discord_file)

# --- WEB SUNUCUSU (Render Ping İçin) ---

app = Flask('')

@app.route('/')
def home():
    return "Bot aktif"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# --- ÇALIŞTIRMA ---

if __name__ == "__main__":
    keep_alive()
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("HATA: DISCORD_TOKEN çevre değişkeni bulunamadı!")
