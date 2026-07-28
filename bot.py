import os
import asyncio
import discord
from discord.ext import commands
import wavelink

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="s!",
    intents=intents,
    help_command=None
)


@bot.event
async def on_ready():
    print("=" * 40)
    print(f"🤖 Bot conectado: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🌐 Servidores: {len(bot.guilds)}")
    print("=" * 40)

    await bot.change_presence(
        activity=discord.Seeing(
            name="s!ayuda $$$"
        )
    )


async def cargar_extensiones():

    extensiones = [
        "cogs.moderacion",
        "cogs.afk",
        "cogs.bienvenida",
        "cogs.logs",
        "cogs.tickets",
        "cogs.verificacion",
        "cogs.utilidades",
        "cogs.antispam",
        "cogs.status",
    ]

    for extension in extensiones:
        try:
            await bot.load_extension(extension)
            print(f"✅ Cargado: {extension}")

        except Exception as error:
            print(f"❌ Error en {extension}: {error}")


async def main():

    if not TOKEN:
        print("❌ ERROR: No existe la variable DISCORD_TOKEN")
        return

    await cargar_extensiones()

    await conectar_lavalink()

    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())