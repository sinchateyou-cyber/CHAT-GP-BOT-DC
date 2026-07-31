import os
import asyncio
import threading
import discord
from discord.ext import commands
from flask import Flask
# ============================================================
# SERVIDOR WEB PARA HOSTING
# ============================================================
app = Flask(__name__)
@app.route("/")
def home():
    return "Bot online"
def run_web():
    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )
    app.run(
        host="0.0.0.0",
        port=port
    )
# ============================================================
# TOKEN
# ============================================================
TOKEN = os.getenv(
    "DISCORD_TOKEN"
)
# ============================================================
# ID DEL SERVIDOR DE PRUEBA
# ============================================================
GUILD_ID = 1529314985174368438
# ============================================================
# INTENTS
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
# ============================================================
# BOT
# ============================================================
class MiBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
    # ========================================================
    # CARGAR COGS
    # ========================================================
    async def setup_hook(self):
        extensiones = [
            "cogs.lock",
            "cogs.avatar",
            "cogs.antilink",
            "cogs.antiflood",
            "cogs.antispam",
            "cogs.owner",
            "cogs.ban",
            "cogs.kick",
            "cogs.timeout",
            "cogs.untimeout",
            "cogs.unlock",
            "cogs.afk",
            "cogs.bienvenida",
            "cogs.logs",
            "cogs.tickets",
            "cogs.verification",
            "cogs.utilidades",
            "cogs.canales",
            "cogs.say",
            "cogs.nick",
            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            "cogs.setstatus",
            "cogs.invite",
            "cogs.help",
            "cogs.clear",
            "cogs.addemoji",
            "cogs.invites",
            "cogs.invites_command",
            "cogs.invites_leaderboard",
            "cogs.botinfo",
            "cogs.config",
            "cogs.social",
            "cogs.key",
            "cogs.status",
            # =================================================
            # SISTEMA DE XP
            # =================================================
            "cogs.xp",
            # =================================================
            # MÚSICA
            # =================================================
            "cogs.play",
            "cogs.stop",
            "cogs.leave",
            # =================================================
            # SERVER SETUP
            # =================================================
            "cogs.server_setup"
        ]
        # ====================================================
        # CARGAR CADA COG
        # ====================================================
        for extension in extensiones:
            try:
                await self.load_extension(
                    extension
                )
                print(
                    f"✅ Cargado: "
                    f"{extension}"
                )
            except Exception as error:
                print(
                    f"❌ Error en "
                    f"{extension}: "
                    f"{error}"
                )
        # ====================================================
        # SINCRONIZAR COMANDOS
        # ====================================================
        try:
            # ------------------------------------------------
            # SERVIDOR DE PRUEBA
            # ------------------------------------------------
            guild = discord.Object(
                id=GUILD_ID
            )
            # Copiar comandos globales
            # al servidor de prueba
            self.tree.copy_global_to(
                guild=guild
            )
            # Sincronizar inmediatamente
            # en el servidor de prueba
            guild_synced = await self.tree.sync(
                guild=guild
            )
            print(
                "✅ Comandos sincronizados "
                "en servidor de prueba: "
                f"{len(guild_synced)}"
            )
            # ------------------------------------------------
            # COMANDOS GLOBALES
            # ------------------------------------------------
            global_synced = await self.tree.sync()
            print(
                "🌎 Comandos globales "
                "sincronizados: "
                f"{len(global_synced)}"
            )
        except Exception as error:
            print(
                "❌ Error sincronizando "
                f"comandos: {error}"
            )
# ============================================================
# CREAR BOT
# ============================================================
bot = MiBot()
# ============================================================
# EVENTO: BOT LISTO
# ============================================================
@bot.event
async def on_ready():
    print(
        "=" * 50
    )
    print(
        f"🤖 Bot conectado: "
        f"{bot.user}"
    )
    print(
        f"🆔 ID: "
        f"{bot.user.id}"
    )
    print(
        f"🌐 Servidores: "
        f"{len(bot.guilds)}"
    )
    print(
        "=" * 50
    )
    # ========================================================
    # ESTADO DEL BOT
    # ========================================================
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="/help 💎"
        )
    )
# ============================================================
# INICIAR BOT
# ============================================================
async def main():
    # ========================================================
    # COMPROBAR TOKEN
    # ========================================================
    if not TOKEN:
        print(
            "❌ ERROR: No existe la variable "
            "DISCORD_TOKEN"
        )
        return
    # ========================================================
    # INICIAR SERVIDOR WEB
    # ========================================================
    threading.Thread(
        target=run_web,
        daemon=True
    ).start()
    # ========================================================
    # INICIAR BOT
    # ========================================================
    await bot.start(
        TOKEN
    )
# ============================================================
# EJECUTAR
# ============================================================
if __name__ == "__main__":
    asyncio.run(
        main()
    )