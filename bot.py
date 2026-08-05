import os
import asyncio
import threading
import secrets
import json
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
# ID OPCIONAL DE TU SERVIDOR PARA SINCRONIZACIÓN RÁPIDA
# En Render podés crear:
# TEST_GUILD_ID = ID_DE_TU_SERVIDOR
#
# Si está vacío, solamente se hará sincronización global.
TEST_GUILD_ID = os.getenv(
    "TEST_GUILD_ID"
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
# OAUTH2 DISCORD
# ============================================================
DISCORD_API = "https://discord.com/api"
DISCORD_OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
)
# ============================================================
# COMPROBAR LOGIN
# ============================================================
def is_logged_in():
    return "user" in session
# ============================================================
# OBTENER COG DE SEGURIDAD
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
# LOGIN
# ============================================================
@app.route("/login")
def login():
    if not DISCORD_CLIENT_ID:
        return (
            "<h1>Error</h1>"
            "<p>Falta DISCORD_CLIENT_ID.</p>",
            500
        )
    if not DISCORD_REDIRECT_URI:
        return (
            "<h1>Error</h1>"
            "<p>Falta DISCORD_REDIRECT_URI.</p>",
            500
        )
    state = secrets.token_urlsafe(
        32
    )
    session[
        "oauth_state"
    ] = state
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
        + urlencode(
            params
        )
    )
    return redirect(
        oauth_url
    )
# ============================================================
# CALLBACK OAUTH2
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
            <p>{error}</p>
            <a href="/">Volver</a>
            """,
            400
        )
    code = request.args.get(
        "code"
    )
    if not code:
        return (
            "<h1>Error</h1>"
            "<p>No se recibió el código.</p>",
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
            "<h1>Error de seguridad</h1>"
            "<p>El estado OAuth2 no coincide.</p>",
            400
        )
    session.pop(
        "oauth_state",
        None
    )
    # ========================================================
    # ACCESS TOKEN
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
            "❌ Error OAuth2:",
            error
        )
        return (
            "<h1>Error de conexión</h1>",
            500
        )
    if token_response.status_code != 200:
        print(
            "❌ Discord rechazó OAuth2:",
            token_response.text
        )
        return (
            "<h1>Error de autenticación</h1>",
            400
        )
    token_json = (
        token_response.json()
    )
    access_token = token_json.get(
        "access_token"
    )
    if not access_token:
        return (
            "<h1>Error</h1>"
            "<p>No se recibió Access Token.</p>",
            400
        )
    # ========================================================
    # INFORMACIÓN DEL USUARIO
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
            "<h1>Error obteniendo usuario</h1>",
            500
        )
    if user_response.status_code != 200:
        return (
            "<h1>No se pudo verificar tu cuenta.</h1>",
            400
        )
    user = user_response.json()
    # ========================================================
    # GUARDAR SESIÓN
    # ========================================================
    session["user"] = {
        "id":
            user.get("id"),
        "username":
            user.get("username"),
        "global_name":
            user.get("global_name"),
        "avatar":
            user.get("avatar")
    }
    session[
        "access_token"
    ] = access_token
    print(
        "✅ Usuario inició sesión:",
        user.get("username")
    )
    return redirect("/")
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
    return redirect("/")
# ============================================================
# API USUARIO
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
# API ESTADO BOT
# ============================================================
@app.route("/api/status")
def api_status():
    if bot.is_ready():
        return jsonify({
            "online":
                True,
            "bot":
                str(bot.user),
            "bot_id":
                bot.user.id,
            "guilds":
                len(bot.guilds),
            "latency":
                round(
                    bot.latency * 1000
                ),
            "status":
                str(bot.status)
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
# API SERVIDORES
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
            len(guilds),
        "guilds":
            guilds
    })
# ============================================================
# API SERVIDOR
# ============================================================
@app.route(
    "/api/guild/<int:guild_id>"
)
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
                len(guild.channels),
            "role_count":
                len(guild.roles),
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
# API SEGURIDAD
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
        session[
            "user"
        ][
            "id"
        ]
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
        or
        member.guild_permissions.administrator
    ):
        return jsonify({
            "success":
                False,
            "message":
                "No tienes permisos."
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
    return jsonify({
        "success":
            True,
        "security": {
            "antispam":
                bool(
                    antispam_cog
                ),
            "antiflood":
                bool(
                    antiflood_cog
                ),
            "antilink":
                bool(
                    antilink_cog
                )
        }
    })
# ============================================================
# CAMBIAR SEGURIDAD
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
                "Debes iniciar sesión."
        }), 401
    guild = bot.get_guild(
        guild_id
    )
    if guild is None:
        return jsonify({
            "success":
                False,
            "message":
                "Servidor no encontrado."
        }), 404
    user_id = int(
        session[
            "user"
        ][
            "id"
        ]
    )
    member = guild.get_member(
        user_id
    )
    if member is None:
        return jsonify({
            "success":
                False,
            "message":
                "No perteneces al servidor."
        }), 403
    if not (
        member.guild_permissions.manage_guild
        or
        member.guild_permissions.administrator
    ):
        return jsonify({
            "success":
                False,
            "message":
                "No tienes permisos."
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
                "enabled debe ser true o false."
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
                "Sistema desconocido."
        }), 400
    cog = bot.get_cog(
        cog_name
    )
    if cog is None:
        return jsonify({
            "success":
                False,
            "message":
                "El sistema no está cargado."
        }), 500
    if not hasattr(
        cog,
        "config"
    ):
        return jsonify({
            "success":
                False,
            "message":
                "El sistema no tiene configuración compatible."
        }), 500
    cog.config[
        guild_id
    ] = enabled
    print(
        f"🛡️ {security_type.upper()} "
        f"en {guild.name}: "
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
# RUTAS SEGURIDAD
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
# FLASK
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
        use_reloader=False,
        threaded=True
    )
# ============================================================
# INTENTS
# ============================================================


intents = discord.Intents.default()

intents.message_content = True
intents.members = True
intents.presences = True
intents.voice_states = True
# ============================================================
# BOT
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
    # SETUP HOOK
    # ========================================================
    async def setup_hook(
        self
    ):
        print("")
        print("=" * 60)
        print("📦 INICIANDO CARGA DE COGS")
        print("=" * 60)
        extensiones = [
            "cogs.lock",
            "cogs.unlock",
            "cogs.ban",
            "cogs.kick",
            "cogs.timeout",
            "cogs.untimeout",
            "cogs.clear",
            "cogs.antilink",
            "cogs.antiflood",
            "cogs.antispam",
            "cogs.afk",
            "cogs.avatar",
            "cogs.nick",
            "cogs.utilidades",
            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            "cogs.reactionroles",
            "cogs.canales",
            "cogs.bienvenida",
            "cogs.logs",
            "cogs.tickets",
            "cogs.verification",
            "cogs.server_setup",
            "cogs.help",
            "cogs.owner",
            "cogs.invite",
            "cogs.invites",
            "cogs.invites_command",
            "cogs.invites_leaderboard",
            "cogs.botinfo",
            "cogs.config",
            "cogs.addemoji",
            "cogs.social",
            "cogs.key",
            "cogs.status",
            "cogs.play",
            "cogs.stop",
            "cogs.leave",
            "cogs.reglas",
            "cogs.configuracionall",
            "cogs.say",
            "cogs.multimedia"
        ]
        cargados = 0
        errores = 0
        for extension in extensiones:
            try:
                await self.load_extension(
                    extension
                )
                cargados += 1
                print(
                    f"✅ Cargado: {extension}"
                )
            except Exception as error:
                errores += 1
                print(
                    f"❌ ERROR CARGANDO: {extension}"
                )
                print(
                    f"   └─ "
                    f"{type(error).__name__}: "
                    f"{error}"
                )
        print("=" * 60)
        print(
            f"📦 Cogs cargados: {cargados}"
        )
        print(
            f"❌ Cogs con errores: {errores}"
        )
        print("=" * 60)
        # ====================================================
        # REACTION ROLES
        # ====================================================
        try:
            from cogs.reactionroles import RoleView
            if os.path.exists(
                "data/roles.json"
            ):
                with open(
                    "data/roles.json",
                    "r",
                    encoding="utf-8"
                ) as archivo:
                    roles_config = json.load(
                        archivo
                    )
                categorias = roles_config.get(
                    "categorias",
                    {}
                )
                for categoria, datos in categorias.items():
                    try:
                        view = RoleView(
                            categoria,
                            datos
                        )
                        self.add_view(
                            view
                        )
                        print(
                            f"🔄 Reaction Role registrado: "
                            f"{categoria}"
                        )
                    except Exception as error:
                        print(
                            f"❌ Error Reaction Role "
                            f"{categoria}: "
                            f"{error}"
                        )
        except Exception as error:
            print(
                "⚠️ Reaction Roles no disponibles:",
                error
            )
        # ====================================================
        # SINCRONIZACIÓN DE SLASH COMMANDS
        # ====================================================
        print("")
        print("=" * 60)
        print("🔄 SINCRONIZANDO SLASH COMMANDS")
        print("=" * 60)
        # ----------------------------------------------------
        # SINCRONIZACIÓN RÁPIDA PARA SERVIDOR DE PRUEBA
        # ----------------------------------------------------
        if TEST_GUILD_ID:
            try:
                guild_id = int(
                    TEST_GUILD_ID
                )
                guild = discord.Object(
                    id=guild_id
                )
                print(
                    f"⚡ Sincronizando comandos "
                    f"en servidor de prueba: "
                    f"{guild_id}"
                )
                self.tree.copy_global_to(
                    guild=guild
                )
                synced_guild = await self.tree.sync(
                    guild=guild
                )
                print(
                    f"✅ Comandos sincronizados "
                    f"en servidor de prueba: "
                    f"{len(synced_guild)}"
                )
            except Exception as error:
                print(
                    "❌ ERROR SYNC SERVIDOR:"
                )
                print(
                    f"{type(error).__name__}: "
                    f"{error}"
                )
        # ----------------------------------------------------
        # SINCRONIZACIÓN GLOBAL
        # ----------------------------------------------------
        try:
            print(
                "🌎 Sincronizando comandos globales..."
            )
            synced = await self.tree.sync()
            print(
                f"🌎 Comandos globales sincronizados: "
                f"{len(synced)}"
            )
            print("")
            print("📋 COMANDOS DISPONIBLES:")
            for command in synced:
                print(
                    f"   /{command.name}"
                )
        except Exception as error:
            print(
                "❌ ERROR SINCRONIZANDO COMANDOS:"
            )
            print(
                f"{type(error).__name__}: "
                f"{error}"
            )
        print("=" * 60)
# ============================================================
# CREAR BOT
# ============================================================
bot = MiBot()
# ============================================================
# COMANDO DE PRUEBA
# ============================================================
@bot.tree.command(
    name="test",
    description="Comprueba si el bot responde."
)
async def test(
    interaction: discord.Interaction
):
    print("")
    print("=" * 60)
    print(
        "🟢 /test RECIBIDO"
    )
    print(
        f"👤 Usuario: "
        f"{interaction.user}"
    )
    print(
        f"🏠 Servidor: "
        f"{interaction.guild}"
    )
    print(
        f"🆔 Guild ID: "
        f"{interaction.guild_id}"
    )
    print("=" * 60)
    try:
        await interaction.response.send_message(
            "✅ ¡El bot responde correctamente!"
        )
        print(
            "🟢 /test RESPONDIDO CORRECTAMENTE"
        )
    except Exception as error:
        print(
            "🔴 ERROR ENVIANDO /test:"
        )
        print(
            f"{type(error).__name__}: "
            f"{error}"
        )
# ============================================================
# EVENTO ON_CONNECT
# ============================================================
@bot.event
async def on_connect():
    print("")
    print("=" * 60)
    print(
        "🟡 BOT CONECTADO AL DISCORD GATEWAY"
    )
    print("=" * 60)
# ============================================================
# EVENTO READY
# ============================================================
@bot.event
async def on_ready():
    print("")
    print("=" * 60)
    print(
        f"🟢 BOT READY: "
        f"{bot.user}"
    )
    print(
        f"🆔 ID: "
        f"{bot.user.id}"
    )
    print(
        f"🌐 SERVIDORES: "
        f"{len(bot.guilds)}"
    )
    print(
        f"📡 LATENCIA: "
        f"{round(bot.latency * 1000)} ms"
    )
    print(
        f"📊 STATUS: "
        f"{bot.status}"
    )
    print("=" * 60)
    print(
        "✅ Dashboard conectado."
    )
    print(
        "🔐 OAuth2 activado."
    )
    print(
        "🛡️ Seguridad activada."
    )
    print(
        "🎭 Reaction Roles activados."
    )
    print(
    "💬 Message Content Intent activado."
)

print(
    "👥 Members Intent activado."
)

print(
    "🟣 Presence Intent activado."
)
# ============================================================
# ERROR PREFIX
# ============================================================
@bot.event
async def on_command_error(
    ctx,
    error
):
    if isinstance(
        error,
        commands.CommandNotFound
    ):
        print(
            f"⚠️ Comando desconocido: "
            f"{ctx.message.content}"
        )
        return
    if isinstance(
        error,
        commands.MissingPermissions
    ):
        await ctx.send(
            "❌ No tenés permisos.",
            delete_after=8
        )
        return
    if isinstance(
        error,
        commands.MissingRequiredArgument
    ):
        await ctx.send(
            "❌ Faltan argumentos.",
            delete_after=8
        )
        return
    print(
        "❌ ERROR COMANDO PREFIX:"
    )
    print(
        f"{type(error).__name__}: "
        f"{error}"
    )
# ============================================================
# ERROR SLASH
# ============================================================
@bot.tree.error
async def on_app_command_error(
    interaction,
    error
):
    print("")
    print("=" * 60)
    print(
        "❌ ERROR SLASH COMMAND"
    )
    print(
        f"Tipo: "
        f"{type(error).__name__}"
    )
    print(
        f"Error: "
        f"{error}"
    )
    print("=" * 60)
    try:
        if interaction.response.is_done():
            await interaction.followup.send(
                "❌ Ocurrió un error ejecutando el comando.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Ocurrió un error ejecutando el comando.",
                ephemeral=True
            )
    except Exception as send_error:
        print(
            "❌ ERROR ENVIANDO MENSAJE DE ERROR:",
            send_error
        )
# ============================================================
# MAIN
# ============================================================
async def main():
    print("")
    print("=" * 60)
    print(
        "🚀 INICIANDO BOT"
    )
    print("=" * 60)
    # ========================================================
    # COMPROBAR TOKEN
    # ========================================================
    if not TOKEN:
        print(
            "❌ ERROR: Falta DISCORD_TOKEN."
        )
        return
    print(
        "🔑 TOKEN ENCONTRADO"
    )
    print(
        f"🔑 Longitud del token: "
        f"{len(TOKEN)}"
    )
    print(
        f"📦 discord.py: "
        f"{discord.__version__}"
    )
    # ========================================================
    # COMPROBAR TEST GUILD
    # ========================================================
    if TEST_GUILD_ID:
        print(
            f"⚡ TEST_GUILD_ID configurado: "
            f"{TEST_GUILD_ID}"
        )
    else:
        print(
            "🌎 TEST_GUILD_ID no configurado."
            " Se usará sincronización global."
        )
    # ========================================================
    # INICIAR FLASK
    # ========================================================
    try:
        web_thread = threading.Thread(
            target=run_web,
            daemon=True
        )
        web_thread.start()
        print(
            "🌐 Flask iniciado correctamente."
        )
        print(
            f"🌐 Puerto: "
            f"{PORT}"
        )
    except Exception as error:
        print(
            "❌ ERROR INICIANDO FLASK"
        )
        print(
            f"{type(error).__name__}: "
            f"{error}"
        )
        import traceback
        traceback.print_exc()
    # ========================================================
    # INICIAR DISCORD
    # ========================================================
    print("")
    print("=" * 60)
    print(
        "🔵 PASO 1: EJECUTANDO bot.start()"
    )
    print("=" * 60)
    try:
        await bot.start(
            TOKEN
        )
        print(
            "🔵 PASO 2: bot.start() FINALIZÓ"
        )
    except discord.LoginFailure:
        print("")
        print("=" * 60)
        print(
            "❌ TOKEN INVÁLIDO"
        )
        print(
            "❌ Revisá DISCORD_TOKEN en Render."
        )
        print("=" * 60)
    except discord.PrivilegedIntentsRequired as error:
        print("")
        print("=" * 60)
        print(
            "❌ ERROR DE PRIVILEGED INTENTS"
        )
        print(
            "❌ Activá los intents necesarios "
            "en Discord Developer Portal."
        )
        print(
            f"Detalles: "
            f"{error}"
        )
        print("=" * 60)
    except discord.HTTPException as error:
        print("")
        print("=" * 60)
        print(
            "❌ ERROR HTTP DE DISCORD"
        )
        print(
            f"Status: "
            f"{error.status}"
        )
        print(
            f"Detalles: "
            f"{error}"
        )
        print("=" * 60)
    except discord.ConnectionClosed as error:
        print("")
        print("=" * 60)
        print(
            "❌ DISCORD CERRÓ LA CONEXIÓN"
        )
        print(
            f"Detalles: "
            f"{error}"
        )
        print("=" * 60)
    except asyncio.CancelledError:
        print(
            "🛑 Conexión cancelada."
        )
        raise
    except Exception as error:
        print("")
        print("=" * 60)
        print(
            "❌ ERROR FATAL DEL BOT"
        )
        print(
            f"Tipo: "
            f"{type(error).__name__}"
        )
        print(
            f"Error: "
            f"{error}"
        )
        print("=" * 60)
        import traceback
        traceback.print_exc()
    finally:
        print("")
        print("=" * 60)
        print(
            "🛑 CONEXIÓN DEL BOT FINALIZADA"
        )
        print("=" * 60)
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
            "🛑 Bot detenido manualmente."
        )
    except Exception as error:
        print("")
        print("=" * 60)
        print(
            "❌ ERROR FATAL FUERA DE MAIN"
        )
        print(
            f"Tipo: "
            f"{type(error).__name__}"
        )
        print(
            f"Error: "
            f"{error}"
        )
        print("=" * 60)
        import traceback
        traceback.print_exc()