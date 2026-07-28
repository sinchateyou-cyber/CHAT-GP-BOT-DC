import os
import asyncio
import discord
from discord.ext import commands
# =========================
# TOKEN
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")
# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
# =========================
# BOT
# =========================
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)
# =========================
# BOT LISTO
# =========================
@bot.event
async def on_ready():
    print("=" * 40)
    print(f"🤖 Bot conectado: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🌐 Servidores: {len(bot.guilds)}")
    # =========================
    # SINCRONIZAR SLASH COMMANDS
    # =========================
    try:
        synced = await bot.tree.sync()
        print(
            f"✅ Slash Commands sincronizados: "
            f"{len(synced)}"
        )
    except Exception as error:
        print(
            f"❌ Error sincronizando Slash Commands: "
            f"{error}"
        )
    print("=" * 40)
    # =========================
    # ESTADO DEL BOT
    # =========================
    await bot.change_presence(
        activity=discord.Seeing(
            name="/help 💎"
        )
    )
# =========================
# CARGAR EXTENSIONES
# =========================
async def cargar_extensiones():
    extensiones = [
        # Moderación
        "cogs.moderacion",
        # Sistemas
        "cogs.afk",
        "cogs.bienvenida",
        "cogs.logs",
        "cogs.tickets",
        "cogs.verificado",
        "cogs.antispam",
        # Utilidades
        "cogs.utilidades",
        "cogs.canales",
        "cogs.say",
        "cogs.owner",
        "cogs.nick",
        # Roles
        "cogs.roles",
        # Status
        "cogs.status",
        # Invitaciones
        "cogs.invite",
        # Ayuda
        "cogs.help",
    ]
    for extension in extensiones:
        try:
            await bot.load_extension(
                extension
            )
            print(
                f"✅ Cargado: {extension}"
            )
        except Exception as error:
            print(
                f"❌ Error en {extension}: "
                f"{error}"
            )
# =========================
# MAIN
# =========================
async def main():
    if not TOKEN:
        print(
            "❌ ERROR: No existe la variable "
            "DISCORD_TOKEN"
        )
        return
    # Cargar todos los Cogs
    await cargar_extensiones()
    # Iniciar bot
    await bot.start(
        TOKEN
    )
# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    asyncio.run(
        main()
    )