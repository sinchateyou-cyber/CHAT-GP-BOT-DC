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
DISCORD_API = "https://discord.com/api"
DISCORD_OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
)
# ============================================================
# PÁGINA PRINCIPAL
# ============================================================
@app.route("/")
def home():
    # Si no inició sesión,
    # mostramos el Dashboard igualmente.
    #
    # Más adelante podemos hacer que
    # obligatoriamente tenga que iniciar sesión.
    return render_template(
        "index.html"
    )
# ============================================================
# LOGIN CON DISCORD
# ============================================================
@app.route("/login")
def login():
    if not DISCORD_CLIENT_ID:
        return """
        <h1>Error de configuración</h1>
        <p>Falta DISCORD_CLIENT_ID en Render.</p>
        """, 500
    if not DISCORD_REDIRECT_URI:
        return """
        <h1>Error de configuración</h1>
        <p>Falta DISCORD_REDIRECT_URI en Render.</p>
        """, 500
    # Guardar estado de seguridad
    # para evitar ataques CSRF
    state = secrets.token_urlsafe(
        32
    )
    session["oauth_state"] = state
    # Parámetros OAuth2
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
    # Crear URL de Discord
    from urllib.parse import urlencode
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
    # Comprobar error de Discord
    error = request.args.get(
        "error"
    )
    if error:
        return f"""
        <h1>Login cancelado</h1>
        <p>
        Discord devolvió:
        {error}
        </p>
        <a href="/">
        Volver al Dashboard
        </a>
        """, 400
    # Obtener código
    code = request.args.get(
        "code"
    )
    if not code:
        return """
        <h1>Error de autenticación</h1>
        <p>
        No se recibió el código de Discord.
        </p>
        """, 400
    # Comprobar estado CSRF
    state = request.args.get(
        "state"
    )
    saved_state = session.get(
        "oauth_state"
    )
    if not state or state != saved_state:
        return """
        <h1>Error de seguridad</h1>
        <p>
        El estado OAuth2 no coincide.
        Intentá iniciar sesión nuevamente.
        </p>
        """, 400
    # Eliminar estado usado
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
        return """
        <h1>Error de conexión</h1>
        <p>
        No se pudo conectar con Discord.
        </p>
        """, 500
    if token_response.status_code != 200:
        print(
            "❌ Error OAuth2:",
            token_response.text
        )
        return """
        <h1>Error de autenticación</h1>
        <p>
        Discord rechazó la autenticación.
        Revisá la configuración OAuth2.
        </p>
        """, 400
    token_json = token_response.json()
    access_token = token_json.get(
        "access_token"
    )
    if not access_token:
        return """
        <h1>Error</h1>
        <p>
        No se recibió el Access Token.
        </p>
        """, 400
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
        return """
        <h1>Error</h1>
        <p>
        No se pudo obtener tu información de Discord.
        </p>
        """, 500
    if user_response.status_code != 200:
        return """
        <h1>Error</h1>
        <p>
        No se pudo verificar tu cuenta de Discord.
        </p>
        """, 400
    user = user_response.json()
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
    # Guardar Access Token
    # para futuras funciones OAuth
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
        username = session[
            "user"
        ].get(
            "username"
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
    # Comprobar login
    if "user" not in session:
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
@app.route(
    "/api/guild/<int:guild_id>"
)
def api_guild(
    guild_id
):
    # Comprobar login
    if "user" not in session:
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
    # CARGAR COGS
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
        # CARGAR TODOS LOS COGS
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
        # SINCRONIZAR COMANDOS SLASH
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
                    f"   /"
                    f"{command.name}"
                )
        except Exception as error:
            print(
                "❌ Error sincronizando "
                f"comandos: "
                f"{error}"
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
        "🌐 API disponible."
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