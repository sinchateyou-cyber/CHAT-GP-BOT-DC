import os
import asyncio
import threading
import secrets
import discord
from discord.ext import commands
from flask import (
    Flask,
    jsonify,
    render_template,
    redirect,
    request,
    session
)
import requests
# ============================================================
# CONFIGURACIÓN
# ============================================================
TOKEN = os.getenv("DISCORD_TOKEN")
PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)
DISCORD_CLIENT_ID = os.getenv(
    "DISCORD_CLIENT_ID"
)
DISCORD_CLIENT_SECRET = os.getenv(
    "DISCORD_CLIENT_SECRET"
)
DISCORD_REDIRECT_URI = os.getenv(
    "DISCORD_REDIRECT_URI"
)
SESSION_SECRET = os.getenv(
    "SESSION_SECRET"
)
if not SESSION_SECRET:
    SESSION_SECRET = secrets.token_hex(32)
# ============================================================
# SERVIDOR WEB / DASHBOARD
# ============================================================
app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static"
)
app.secret_key = SESSION_SECRET
# ============================================================
# CONFIGURACIÓN OAUTH2 DISCORD
# ============================================================
DISCORD_API = (
    "https://discord.com/api"
)
DISCORD_OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
)
# ============================================================
# FUNCIÓN: COMPROBAR LOGIN
# ============================================================
def is_logged_in():
    return (
        "user" in session
    )
# ============================================================
# FUNCIÓN: OBTENER COG DE SEGURIDAD
# ============================================================
def get_security_cog(
    guild_id,
    cog_name
):
    if not bot.is_ready():
        return None, (
            "El bot todavía no está listo."
        )
    guild = bot.get_guild(
        int(guild_id)
    )
    if guild is None:
        return None, (
            "El bot no está en este servidor."
        )
    cog = bot.get_cog(
        cog_name
    )
    if cog is None:
        return None, (
            f"El sistema {cog_name} "
            "no está cargado."
        )
    return cog, None
# ============================================================
# PÁGINA PRINCIPAL
# ============================================================
@app.route("/")
def home():
    return render_template(
        "index.html"
    )
# ============================================================
# LOGIN CON DISCORD
# ============================================================
@app.route("/login")
def login():
    if not DISCORD_CLIENT_ID:
        return (
            """
            <h1>Error de configuración</h1>
            <p>
            Falta DISCORD_CLIENT_ID en Render.
            </p>
            """,
            500
        )
    if not DISCORD_REDIRECT_URI:
        return (
            """
            <h1>Error de configuración</h1>
            <p>
            Falta DISCORD_REDIRECT_URI en Render.
            </p>
            """,
            500
        )
    state = secrets.token_urlsafe(32)
    session["oauth_state"] = state
    from urllib.parse import urlencode
    params = {
        "client_id":
            DISCORD_CLIENT_ID,
        "redirect_uri":
            DISCORD_REDIRECT_URI,
        "response_type":
            "code",
        "scope":
            "identify guilds",
        "state":
            state
    }
    oauth_url = (
        DISCORD_OAUTH_URL
        + "?"
        + urlencode(params)
    )
    return redirect(
        oauth_url
    )
# ============================================================
# CALLBACK DE DISCORD
# ============================================================
@app.route("/auth/callback")
def oauth_callback():
    error = request.args.get(
        "error"
    )
    if error:
        return (
            f"""
            <h1>Login cancelado</h1>
            <p>
            Discord devolvió:
            {error}
            </p>
            <a href="/">
            Volver al Dashboard
            </a>
            """,
            400
        )
    code = request.args.get(
        "code"
    )
    if not code:
        return (
            """
            <h1>Error de autenticación</h1>
            <p>
            No se recibió el código de Discord.
            </p>
            """,
            400
        )
    state = request.args.get(
        "state"
    )
    saved_state = session.get(
        "oauth_state"
    )
    if (
        not state
        or state != saved_state
    ):
        return (
            """
            <h1>Error de seguridad</h1>
            <p>
            El estado OAuth2 no coincide.
            </p>
            """,
            400
        )
    session.pop(
        "oauth_state",
        None
    )
    # ========================================================
    # OBTENER ACCESS TOKEN
    # ========================================================
    token_data = {
        "client_id":
            DISCORD_CLIENT_ID,
        "client_secret":
            DISCORD_CLIENT_SECRET,
        "grant_type":
            "authorization_code",
        "code":
            code,
        "redirect_uri":
            DISCORD_REDIRECT_URI
    }
    try:
        token_response = requests.post(
            f"{DISCORD_API}/oauth2/token",
            data=token_data,
            headers={
                "Content-Type":
                    "application/x-www-form-urlencoded"
            },
            timeout=10
        )
    except requests.RequestException as error:
        print(
            "❌ Error conectando con Discord:",
            error
        )
        return (
            """
            <h1>Error de conexión</h1>
            <p>
            No se pudo conectar con Discord.
            </p>
            """,
            500
        )
    if token_response.status_code != 200:
        print(
            "❌ Error OAuth2:",
            token_response.text
        )
        return (
            """
            <h1>Error de autenticación</h1>
            <p>
            Discord rechazó la autenticación.
            </p>
            """,
            400
        )
    token_json = (
        token_response.json()
    )
    access_token = (
        token_json.get(
            "access_token"
        )
    )
    if not access_token:
        return (
            """
            <h1>Error</h1>
            <p>
            No se recibió el Access Token.
            </p>
            """,
            400
        )
    # ========================================================
    # OBTENER INFORMACIÓN DEL USUARIO
    # ========================================================
    headers = {
        "Authorization":
            f"Bearer {access_token}"
    }
    try:
        user_response = requests.get(
            f"{DISCORD_API}/users/@me",
            headers=headers,
            timeout=10
        )
    except requests.RequestException as error:
        print(
            "❌ Error obteniendo usuario:",
            error
        )
        return (
            """
            <h1>Error</h1>
            <p>
            No se pudo obtener tu información.
            </p>
            """,
            500
        )
    if user_response.status_code != 200:
        return (
            """
            <h1>Error</h1>
            <p>
            No se pudo verificar tu cuenta.
            </p>
            """,
            400
        )
    user = (
        user_response.json()
    )
    # ========================================================
    # GUARDAR SESIÓN
    # ========================================================
    session["user"] = {
        "id":
            user.get(
                "id"
            ),
        "username":
            user.get(
                "username"
            ),
        "global_name":
            user.get(
                "global_name"
            ),
        "avatar":
            user.get(
                "avatar"
            )
    }
    session["access_token"] = access_token
    print(
        "✅ Usuario inició sesión:",
        user.get(
            "username"
        )
    )
    return redirect(
        "/"
    )
# ============================================================
# LOGOUT
# ============================================================
@app.route("/logout")
def logout():
    username = None
    if "user" in session:
        username = (
            session["user"].get(
                "username"
            )
        )
    session.clear()
    print(
        "👋 Usuario cerró sesión:",
        username
    )
    return redirect(
        "/"
    )
# ============================================================
# API: USUARIO ACTUAL
# ============================================================
@app.route("/api/me")
def api_me():
    user = session.get(
        "user"
    )
    if not user:
        return jsonify({
            "logged_in":
                False,
            "user":
                None
        })
    return jsonify({
        "logged_in":
            True,
        "user":
            user
    })
# ============================================================
# API: ESTADO DEL BOT
# ============================================================
@app.route("/api/status")
def api_status():
    if bot.is_ready():
        return jsonify({
            "online":
                True,
            "bot":
                str(
                    bot.user
                ),
            "bot_id":
                bot.user.id,
            "guilds":
                len(
                    bot.guilds
                ),
            "latency":
                round(
                    bot.latency * 1000
                ),
            "status":
                str(
                    bot.status
                )
        })
    return jsonify({
        "online":
            False,
        "bot":
            None,
        "bot_id":
            None,
        "guilds":
            0,
        "latency":
            None,
        "status":
            "offline"
    })
# ============================================================
# API: LISTA DE SERVIDORES
# ============================================================
@app.route("/api/guilds")
def api_guilds():
    if not is_logged_in():
        return jsonify({
            "success":
                False,
            "message":
                "Debes iniciar sesión con Discord.",
            "guilds":
                []
        }), 401
    if not bot.is_ready():
        return jsonify({
            "success":
                False,
            "message":
                "El bot todavía no está listo.",
            "guilds":
                []
        }), 503
    guilds = []
    for guild in bot.guilds:
        guilds.append({
            "id":
                guild.id,
            "name":
                guild.name,
            "member_count":
                guild.member_count,
            "icon": (
                str(
                    guild.icon.url
                )
                if guild.icon
                else None
            )
        })
    return jsonify({
        "success":
            True,
        "count":
            len(
                guilds
            ),
        "guilds":
            guilds
    })
# ============================================================
# API: INFORMACIÓN DE UN SERVIDOR
# ============================================================
@app.route("/api/guild/<int:guild_id>")
def api_guild(
    guild_id
):
    if not is_logged_in():
        return jsonify({
            "success":
                False,
            "message":
                "Debes iniciar sesión con Discord."
        }), 401
    if not bot.is_ready():
        return jsonify({
            "success":
                False,
            "message":
                "El bot todavía no está listo."
        }), 503
    guild = bot.get_guild(
        guild_id
    )
    if guild is None:
        return jsonify({
            "success":
                False,
            "message":
                "El bot no está en este servidor."
        }), 404
    return jsonify({
        "success":
            True,
        "guild": {
            "id":
                guild.id,
            "name":
                guild.name,
            "member_count":
                guild.member_count,
            "channel_count":
                len(
                    guild.channels
                ),
            "role_count":
                len(
                    guild.roles
                ),
            "icon": (
                str(
                    guild.icon.url
                )
                if guild.icon
                else None
            )
        }
    })
# ============================================================
# API: SEGURIDAD
# ============================================================
@app.route(
    "/api/security/<int:guild_id>",
    methods=["GET"]
)
def api_security(
    guild_id
):
    if not is_logged_in():
        return jsonify({
            "success":
                False,
            "message":
                "Debes iniciar sesión con Discord."
        }), 401
    guild = bot.get_guild(
        guild_id
    )
    if guild is None:
        return jsonify({
            "success":
                False,
            "message":
                "El bot no está en este servidor."
        }), 404
    user_id = int(
        session["user"]["id"]
    )
    member = guild.get_member(
        user_id
    )
    if member is None:
        return jsonify({
            "success":
                False,
            "message":
                "No perteneces a este servidor."
        }), 403
    if not (
        member.guild_permissions.manage_guild
        or member.guild_permissions.administrator
    ):
        return jsonify({
            "success":
                False,
            "message":
                "No tienes permisos para administrar este servidor."
        }), 403
    antispam_cog = bot.get_cog(
        "AntiSpam"
    )
    antiflood_cog = bot.get_cog(
        "AntiFlood"
    )
    antilink_cog = bot.get_cog(
        "AntiLink"
    )
    antispam_enabled = False
    antiflood_enabled = False
    antilink_enabled = False
    if antispam_cog:
        antispam_enabled = (
            antispam_cog.config.get(
                guild_id,
                False
            )
        )
    if antiflood_cog:
        antiflood_enabled = (
            antiflood_cog.config.get(
                guild_id,
                False
            )
        )
    if antilink_cog:
        antilink_enabled = (
            antilink_cog.config.get(
                guild_id,
                False
            )
        )
    return jsonify({
        "success":
            True,
        "security": {
            "antispam":
                antispam_enabled,
            "antiflood":
                antiflood_enabled,
            "antilink":
                antilink_enabled
        }
    })
# ============================================================
# FUNCIÓN PARA CAMBIAR SEGURIDAD
# ============================================================
def change_security(
    guild_id,
    security_type
):
    if not is_logged_in():
        return jsonify({
            "success":
                False,
            "message":
                "Debes iniciar sesión con Discord."
        }), 401
    guild = bot.get_guild(
        guild_id
    )
    if guild is None:
        return jsonify({
            "success":
                False,
            "message":
                "El bot no está en este servidor."
        }), 404
    user_id = int(
        session["user"]["id"]
    )
    member = guild.get_member(
        user_id
    )
    if member is None:
        return jsonify({
            "success":
                False,
            "message":
                "No perteneces a este servidor."
        }), 403
    if not (
        member.guild_permissions.manage_guild
        or member.guild_permissions.administrator
    ):
        return jsonify({
            "success":
                False,
            "message":
                "No tienes permisos para administrar este servidor."
        }), 403
    data = request.get_json(
        silent=True
    )
    if not data:
        return jsonify({
            "success":
                False,
            "message":
                "No se recibieron datos."
        }), 400
    enabled = data.get(
        "enabled"
    )
    if not isinstance(
        enabled,
        bool
    ):
        return jsonify({
            "success":
                False,
            "message":
                "El valor enabled debe ser true o false."
        }), 400
    cog_names = {
        "antispam":
            "AntiSpam",
        "antiflood":
            "AntiFlood",
        "antilink":
            "AntiLink"
    }
    cog_name = cog_names.get(
        security_type
    )
    if not cog_name:
        return jsonify({
            "success":
                False,
            "message":
                "Sistema de seguridad desconocido."
        }), 400
    cog = bot.get_cog(
        cog_name
    )
    if cog is None:
        return jsonify({
            "success":
                False,
            "message":
                f"El sistema {security_type} no está cargado."
        }), 500
    cog.config[
        guild_id
    ] = enabled
    print(
        f"🛡️ {security_type.upper()} "
        f"cambiado en {guild.name}: "
        f"{'ACTIVADO' if enabled else 'DESACTIVADO'}"
    )
    return jsonify({
        "success":
            True,
        "type":
            security_type,
        "guild_id":
            guild_id,
        "enabled":
            enabled
    })
# ============================================================
# ACTIVAR / DESACTIVAR ANTISPAM
# ============================================================
@app.route(
    "/api/security/<int:guild_id>/antispam",
    methods=["POST"]
)
def api_security_antispam(
    guild_id
):
    return change_security(
        guild_id,
        "antispam"
    )
# ============================================================
# ACTIVAR / DESACTIVAR ANTIFLOOD
# ============================================================
@app.route(
    "/api/security/<int:guild_id>/antiflood",
    methods=["POST"]
)
def api_security_antiflood(
    guild_id
):
    return change_security(
        guild_id,
        "antiflood"
    )
# ============================================================
# ACTIVAR / DESACTIVAR ANTILINK
# ============================================================
@app.route(
    "/api/security/<int:guild_id>/antilink",
    methods=["POST"]
)
def api_security_antilink(
    guild_id
):
    return change_security(
        guild_id,
        "antilink"
    )
# ============================================================
# SERVIDOR FLASK
# ============================================================
def run_web():
    print(
        f"🌐 Servidor web iniciado "
        f"en el puerto {PORT}"
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
intents = (
    discord.Intents.default()
)
intents.message_content = True
intents.members = True
intents.voice_states = True
# ============================================================
# CLASE DEL BOT
# ============================================================
class MiBot(
    commands.Bot
):
    def __init__(
        self
    ):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )
    # ========================================================
    # CARGAR COGS Y SINCRONIZAR SLASH COMMANDS
    # ========================================================
    async def setup_hook(
        self
    ):
        extensiones = [
            # MODERACIÓN
            "cogs.lock",
            "cogs.unlock",
            "cogs.ban",
            "cogs.kick",
            "cogs.timeout",
            "cogs.untimeout",
            "cogs.clear",
            # SEGURIDAD
            "cogs.antilink",
            "cogs.antiflood",
            "cogs.antispam",
            # USUARIOS
            "cogs.afk",
            "cogs.avatar",
            "cogs.nick",
            "cogs.utilidades",
            # ROLES
            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            # CANALES
            "cogs.canales",
            # SERVIDOR
            "cogs.reglas",
            "cogs.bienvenida",
            "cogs.logs",
            "cogs.tickets",
            "cogs.verification",
            "cogs.server_setup",
            # COMANDOS
            "cogs.say",
            "cogs.help",
            # OWNER
            "cogs.owner",
            # INVITACIONES
            "cogs.invite",
            "cogs.invites",
            "cogs.invites_command",
            "cogs.invites_leaderboard",
            # INFORMACIÓN
            "cogs.botinfo",
            "cogs.config",
            "cogs.dashboard",
            # PERSONALIZACIÓN
            "cogs.addemoji",
            "cogs.social",
            # KEYS
            "cogs.key",
            # STATUS
            "cogs.status",
            # XP
            "cogs.xp",
            # MÚSICA
            "cogs.play",
            "cogs.stop",
            "cogs.leave"
        ]
        # ====================================================
        # CARGAR COGS
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
                    f"❌ Error cargando "
                    f"{extension}: "
                    f"{error}"
                )
        # ====================================================
        # SINCRONIZAR COMANDOS SLASH GLOBALMENTE
        # ====================================================
        try:
            synced = await self.tree.sync()
            print(
                "🌎 Comandos slash globales "
                f"sincronizados: "
                f"{len(synced)}"
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
        "🔐 Login con Discord activado."
    )
    print(
        "🛡️ API de seguridad activada."
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