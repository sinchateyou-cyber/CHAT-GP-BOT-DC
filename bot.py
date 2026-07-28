import os
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"BOT CONECTADO: {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

@bot.command()
async def hola(ctx):
    await ctx.send(f"👋 Hola {ctx.author.mention}!")

@bot.command()
async def ayuda(ctx):
    await ctx.send(
        "🤖 Comandos:\n"
        "!ping\n"
        "!hola\n"
        "!ayuda"
    )

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    print("ERROR: No existe DISCORD_TOKEN")
else:
    bot.run(TOKEN)