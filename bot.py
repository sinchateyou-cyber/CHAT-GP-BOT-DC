import os
import asyncio
import discord
from discord.ext import commands
# =========================
# TOKEN
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")
# =========================
# ID DEL SERVIDOR
# =========================
GUILD_ID = 1529314985174368438
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
class MiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
    # =========================
    # CARGAR COGS Y SINCRONIZAR
    # =========================
    async def setup_hook(self):
        extensiones = [
            "cogs.moderacion",
            "cogs.afk",
            "cogs.bienvenida",
            "cogs.logs",
            "cogs.tickets",
            "cogs.verificado",
            "cogs.antispam",
            "cogs.utilidades",
            "cogs.canales",
            "cogs.say",
            "cogs.nick",
            "cogs.addrole",
             "cogs.createrole",
             "cogs.deleterole",
            "cogs.status",
            "cogs.invite",
            "cogs.help",
            "cogs.clear",
        ]
        # =========================
        # CARGAR COGS
        # =========================
        for extension in extensiones:
            try:
                await self.load_extension(extension)
                print(f"✅ Cargado: {extension}")
            except Exception as error:
                print(
                    f"❌ Error en {extension}: {error}"
                )
        # =========================
        # SINCRONIZAR SLASH COMMANDS
        # =========================
        guild = discord.Object(id=GUILD_ID)
        try:
            # Copiar comandos globales al servidor
            self.tree.copy_global_to(guild=guild)
            # Sincronizar con el servidor
            synced = await self.tree.sync(guild=guild)
            print(
                f"✅ Slash Commands sincronizados: "
                f"{len(synced)}"
            )
        except Exception as error:
            print(
                f"❌ Error sincronizando comandos: "
                f"{error}"
            )
# =========================
# CREAR BOT
# =========================
bot = MiBot()
# =========================
# BOT LISTO
# =========================
@bot.event
async def on_ready():
    print("=" * 40)
    print(f"🤖 Bot conectado: {bot.user}")
    print(f"🆔 ID: {bot.user.id}")
    print(f"🌐 Servidores: {len(bot.guilds)}")
    print("=" * 40)
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/help 💎"
        )
    )
# =========================
# INICIAR BOT
# =========================
async def main():
    if not TOKEN:
        print(
            "❌ ERROR: No existe la variable "
            "DISCORD_TOKEN"
        )
        return
    await bot.start(TOKEN)
# =========================
# EJECUTAR
# =========================
if __name__ == "__main__":
    asyncio.run(main())