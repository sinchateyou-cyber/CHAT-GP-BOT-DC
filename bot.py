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
            # =================================================
            # MODERACIÓN
            # =================================================
            "cogs.lock",
            "cogs.unlock",
            "cogs.ban",
            "cogs.kick",
            "cogs.timeout",
            "cogs.untimeout",
            "cogs.clear",
            # =================================================
            # SEGURIDAD
            # =================================================
            "cogs.antilink",
            "cogs.antiflood",
            "cogs.antispam",
            # =================================================
            # USUARIOS
            # =================================================
            "cogs.afk",
            "cogs.avatar",
            "cogs.nick",
            "cogs.utilidades",
            # =================================================
            # ROLES Y CANALES
            # =================================================
            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            "cogs.canales",
            # =================================================
            # SERVIDOR
            # =================================================
            "cogs.bienvenida",
            "cogs.logs",
            "cogs.tickets",
            "cogs.verification",
            "cogs.server_setup",
            # =================================================
            # COMANDOS
            # =================================================
            "cogs.say",
            "cogs.help",
            # =================================================
            # OWNER
            # =================================================
            "cogs.owner",
            # =================================================
            # INVITACIONES
            # =================================================
            "cogs.invite",
            "cogs.invites",
            "cogs.invites_command",
            "cogs.invites_leaderboard",
            # =================================================
            # INFORMACIÓN
            # =================================================
            "cogs.botinfo",
            "cogs.config",
            # =================================================
            # PERSONALIZACIÓN
            # =================================================
            "cogs.avatar",
            "cogs.addemoji",
            # =================================================
            # STATUS
            # =================================================
            "cogs.status",
            # =================================================
            # =================================================
            # SOCIAL
            # =================================================
            "cogs.social",
            # =================================================
            # KEYS
            # =================================================
            "cogs.key",
            # =================================================
            # SISTEMA XP
            # =================================================
            "cogs.xp",
            # =================================================
            # MÚSICA
            # =================================================
            "cogs.play",
            "cogs.stop",
            "cogs.leave"
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
                    f"✅ Cargado: {extension}"
                )
            except Exception as error:
                print(
                    f"❌ Error en {extension}: "
                    f"{error}"
                )
        # ====================================================
        # SINCRONIZAR COMANDOS GLOBALMENTE
        # ====================================================
        try:
            synced = await self.tree.sync()
            print(
                "🌎 Comandos slash globales "
                f"sincronizados: {len(synced)}"
            )
            print(
                "📋 Comandos registrados:"
            )
            for command in synced:
                print(
                    f"   /{command.name}"
                )
        except Exception as error:
            print(
                "❌ Error sincronizando "
                f"comandos globales: {error}"
            )
# ============================================================
# CREAR BOT
# ============================================================
bot = MiBot()
# ============================================================
# BOT LISTO
# ============================================================
@bot.event
async def on_ready():
    print(
        "=" * 50
    )
    print(
        f"🤖 Bot conectado: {bot.user}"
    )
    print(
        f"🆔 ID: {bot.user.id}"
    )
    print(
        f"🌐 Servidores: {len(bot.guilds)}"
    )
    print(
        "=" * 50
    )
    print(
        "ℹ️ El estado y la actividad "
        "se controlan manualmente."
    )
    print(
        "👉 Usá /setstatus para cambiar "
        "Online, Ausente o No molestar."
    )
    print(
        "👉 Usá /setactivity para cambiar "
        "la actividad."
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