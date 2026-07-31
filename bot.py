import os
import asyncio
import threading
import discord
from discord.ext import commands
from flask import Flask, jsonify, render_template
# ============================================================
# CONFIGURACIÓN
# ============================================================
TOKEN = os.getenv("DISCORD_TOKEN")
# Puerto asignado automáticamente por Render
PORT = int(os.getenv("PORT", "10000"))
# ============================================================
# SERVIDOR WEB / DASHBOARD
# ============================================================
app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static"
)
# ============================================================
# PÁGINA PRINCIPAL DEL DASHBOARD
# ============================================================
@app.route("/")
def home():
    try:
        return render_template("index.html")
    except Exception:
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <title>Bot Online</title>
        </head>
        <body>
            <h1>🤖 Bot online</h1>
            <p>El bot está funcionando correctamente.</p>
        </body>
        </html>
        """
# ============================================================
# API: ESTADO DEL BOT
# ============================================================
@app.route("/api/status")
def api_status():
    if bot.is_ready():
        return jsonify({
            "online": True,
            "bot": str(bot.user),
            "bot_id": bot.user.id,
            "guilds": len(bot.guilds),
            "latency": round(bot.latency * 1000),
            "status": str(bot.status)
        })
    return jsonify({
        "online": False,
        "bot": None,
        "bot_id": None,
        "guilds": 0,
        "latency": None,
        "status": "offline"
    })
# ============================================================
# API: LISTA DE SERVIDORES
# ============================================================
@app.route("/api/guilds")
def api_guilds():
    if not bot.is_ready():
        return jsonify({
            "success": False,
            "message": "El bot todavía no está listo.",
            "guilds": []
        }), 503
    guilds = []
    for guild in bot.guilds:
        guilds.append({
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
            "icon": (
                str(guild.icon.url)
                if guild.icon
                else None
            )
        })
    return jsonify({
        "success": True,
        "count": len(guilds),
        "guilds": guilds
    })
# ============================================================
# API: INFORMACIÓN DE UN SERVIDOR
# ============================================================
@app.route("/api/guild/<int:guild_id>")
def api_guild(guild_id):
    if not bot.is_ready():
        return jsonify({
            "success": False,
            "message": "El bot todavía no está listo."
        }), 503
    guild = bot.get_guild(guild_id)
    if guild is None:
        return jsonify({
            "success": False,
            "message": "El bot no está en este servidor."
        }), 404
    return jsonify({
        "success": True,
        "guild": {
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
            "channel_count": len(guild.channels),
            "role_count": len(guild.roles),
            "icon": (
                str(guild.icon.url)
                if guild.icon
                else None
            )
        }
    })
# ============================================================
# SERVIDOR FLASK
# ============================================================
def run_web():
    print(
        f"🌐 Servidor web iniciado en el puerto {PORT}"
    )
    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )
# ============================================================
# INTENTS
# ============================================================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True
# ============================================================
# CLASE DEL BOT
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
            # ROLES
            # =================================================
            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            # =================================================
            # CANALES
            # =================================================
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
            "cogs.addemoji",
            "cogs.social",
            # =================================================
            # KEYS
            # =================================================
            "cogs.key",
            # =================================================
            # STATUS
            # =================================================
            "cogs.status",
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
        # CARGAR TODOS LOS COGS
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
                    f"❌ Error cargando "
                    f"{extension}: "
                    f"{error}"
                )
        # ====================================================
        # SINCRONIZAR COMANDOS SLASH
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
        "=" * 60
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
        f"📡 Latencia: "
        f"{round(bot.latency * 1000)} ms"
    )
    print(
        "=" * 60
    )
    print(
        "✅ Dashboard conectado al bot."
    )
    print(
        "🌐 API disponible."
    )
    print(
        "👉 /api/status"
    )
    print(
        "👉 /api/guilds"
    )
    print(
        "👉 /api/guild/<ID>"
    )
# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
async def main():
    # ========================================================
    # COMPROBAR TOKEN
    # ========================================================
    if not TOKEN:
        print(
            "❌ ERROR: No se encontró "
            "DISCORD_TOKEN."
        )
        return
    # ========================================================
    # INICIAR SERVIDOR WEB
    # ========================================================
    web_thread = threading.Thread(
        target=run_web,
        daemon=True
    )
    web_thread.start()
    # ========================================================
    # INICIAR BOT
    # ========================================================
    print(
        "🚀 Iniciando bot..."
    )
    await bot.start(
        TOKEN
    )
# ============================================================
# EJECUTAR
# ============================================================
if __name__ == "__main__":
    try:
        asyncio.run(
            main()
        )
    except KeyboardInterrupt:
        print(
            "🛑 Bot detenido."
        )