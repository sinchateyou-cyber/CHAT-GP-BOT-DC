import os
import asyncio
import threading
import secrets
import json
import traceback
from urllib.parse import urlencode

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
PORT = int(os.getenv("PORT", "10000"))

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")

SESSION_SECRET = os.getenv("SESSION_SECRET")

# ID DEL SERVIDOR DONDE QUERÉS PROBAR LOS COMANDOS
GUILD_ID = 1534290216418938891

# Opcional
TEST_GUILD_ID = os.getenv("TEST_GUILD_ID")

if not SESSION_SECRET:
    SESSION_SECRET = secrets.token_hex(32)

# ============================================================
# FLASK
# ============================================================

app = Flask(
    __name__,
    template_folder="dashboard/templates",
    static_folder="dashboard/static"
)

app.secret_key = SESSION_SECRET

# ============================================================
# DISCORD OAUTH2
# ============================================================

DISCORD_API = "https://discord.com/api"

DISCORD_OAUTH_URL = (
    "https://discord.com/oauth2/authorize"
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

class MiBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.cogs_loaded = []
        self.cogs_failed = []

    # ========================================================
    # SETUP HOOK
    # ========================================================

    async def setup_hook(self):

        print("")
        print("=" * 70)
        print("📦 INICIANDO SETUP DEL BOT")
        print("=" * 70)

        await self.load_all_cogs()

        await self.load_persistent_views()

        async def load_persistent_views(self):

    print("")
    print("=" * 70)
    print("🎭 CARGANDO VIEWS PERSISTENTES")
    print("=" * 70)

    # ========================================================
    # TICKETS
    # ========================================================

    try:

        from cogs.tickets import TicketView

        self.add_view(
            TicketView()
        )

        print(
            "✅ View persistente: Tickets"
        )

    except Exception as error:

        print(
            f"❌ Error cargando Tickets: {error}"
        )

    # ========================================================
    # REACTION ROLES
    # ========================================================

    try:

        from cogs.reactionroles import RoleView

        if not os.path.exists("data/roles.json"):

            print(
                "⚠️ data/roles.json no existe."
            )

            return

        with open(
            "data/roles.json",
            "r",
            encoding="utf-8"
        ) as file:

            roles_config = json.load(file)

        # Tu JSON tiene:
        #
        # {
        #   "1534290216418938891": {
        #       "categorias": {...}
        #   }
        # }

        guild_config = roles_config.get(
            str(GUILD_ID),
            {}
        )

        categorias = guild_config.get(
            "categorias",
            {}
        )

        for categoria, datos in categorias.items():

            try:

                titulo = datos.get(
                    "titulo",
                    categoria
                )

                opciones = datos.get(
                    "roles",
                    {}
                )

                if not opciones:
                    continue

                view = RoleView(
                    categoria,
                    titulo,
                    opciones
                )

                self.add_view(view)

                print(
                    f"✅ View roles registrada: {categoria}"
                )

            except Exception as error:

                print(
                    f"❌ Error View {categoria}: {error}"
                )

    except Exception as error:

        print(
            f"⚠️ No se pudieron cargar "
            f"las views de roles: {error}"
        )

    print("")
    print("=" * 70)
    print("🎭 VIEWS PERSISTENTES CARGADAS")
    print("=" * 70)

    # ========================================================
    # CARGAR COGS
    # ========================================================

    async def load_all_cogs(self):

        extensions = [

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

            "cogs.say",
            "cogs.filtro",
            "cogs.mute",
            "cogs.interacciones",
            "cogs.media_rol",
            "cogs.reactionroles"
        ]

        print("")
        print("=" * 70)
        print("📦 CARGANDO COGS")
        print("=" * 70)

        for extension in extensions:

            try:

                await self.load_extension(extension)

                self.cogs_loaded.append(extension)

                print(
                    f"✅ CARGADO: {extension}"
                )

            except commands.ExtensionAlreadyLoaded:

                print(
                    f"⚠️ YA CARGADO: {extension}"
                )

            except Exception as error:

                self.cogs_failed.append(
                    (extension, error)
                )

                print("")
                print(
                    f"❌ ERROR: {extension}"
                )

                print(
                    f"   Tipo: {type(error).__name__}"
                )

                print(
                    f"   Detalle: {error}"
                )

                traceback.print_exc()

        print("")
        print("=" * 70)
        print(
            f"📦 COGS CARGADOS: {len(self.cogs_loaded)}"
        )
        print(
            f"❌ COGS CON ERROR: {len(self.cogs_failed)}"
        )
        print("=" * 70)

    # ========================================================
    # VIEWS PERSISTENTES
    # ========================================================

    async def load_persistent_views(self):

        print("")
        print("=" * 70)
        print("🎭 CARGANDO VIEWS PERSISTENTES")
        print("=" * 70)

        try:

            from cogs.reactionroles import RoleView

            if not os.path.exists("data/roles.json"):

                print(
                    "⚠️ data/roles.json no existe."
                )

                return

            with open(
                "data/roles.json",
                "r",
                encoding="utf-8"
            ) as file:

                roles_config = json.load(file)

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

                    self.add_view(view)

                    print(
                        f"✅ View registrada: {categoria}"
                    )

                except Exception as error:

                    print(
                        f"❌ Error View {categoria}: "
                        f"{error}"
                    )

        except Exception as error:

            print(
                f"⚠️ No se pudieron cargar "
                f"las views: {error}"
            )

    # ========================================================
    # MOSTRAR COMANDOS
    # ========================================================

    async def show_loaded_commands(self):

        print("")
        print("=" * 70)
        print("📋 COMANDOS CARGADOS")
        print("=" * 70)

        prefix_commands = [
            command
            for command in self.commands
            if not command.hidden
        ]

        slash_commands = self.tree.get_commands()

        print("")
        print(
            f"⌨️ COMANDOS PREFIX: "
            f"{len(prefix_commands)}"
        )

        if prefix_commands:

            for command in sorted(
                prefix_commands,
                key=lambda x: x.name
            ):

                print(
                    f"   !{command.name}"
                )

        else:

            print(
                "   ⚠️ No hay comandos prefix."
            )

        print("")
        print(
            f"⚡ SLASH COMMANDS: "
            f"{len(slash_commands)}"
        )

        if slash_commands:

            for command in sorted(
                slash_commands,
                key=lambda x: x.name
            ):

                print(
                    f"   /{command.name}"
                )

        else:

            print(
                "   ⚠️ No hay slash commands."
            )

        print("")
        print("=" * 70)

    # ========================================================
    # SINCRONIZAR SLASH COMMANDS
    # ========================================================

    async def sync_commands(self):

        print("")
        print("=" * 70)
        print("🔄 SINCRONIZANDO SLASH COMMANDS")
        print("=" * 70)

        try:

            guild = discord.Object(
                id=GUILD_ID
            )

            print(
                f"⚡ Guild principal: {GUILD_ID}"
            )

            self.tree.copy_global_to(
                guild=guild
            )

            synced = await self.tree.sync(
                guild=guild
            )

            print("")
            print(
                f"✅ COMANDOS SINCRONIZADOS: "
                f"{len(synced)}"
            )

            for command in synced:

                print(
                    f"   /{command.name}"
                )

        except Exception as error:

            print("")
            print(
                "❌ ERROR SINCRONIZANDO "
                "GUILD PRINCIPAL"
            )

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

            traceback.print_exc()

        if TEST_GUILD_ID:

            try:

                test_id = int(
                    TEST_GUILD_ID
                )

                test_guild = discord.Object(
                    id=test_id
                )

                self.tree.copy_global_to(
                    guild=test_guild
                )

                synced_test = await self.tree.sync(
                    guild=test_guild
                )

                print("")
                print(
                    f"✅ TEST GUILD {test_id}: "
                    f"{len(synced_test)} comandos"
                )

            except Exception as error:

                print("")
                print(
                    "❌ ERROR TEST_GUILD_ID"
                )

                print(
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        print("")
        print("=" * 70)
        print("🌎 NO SE HACE SYNC GLOBAL")
        print("=" * 70)

# ============================================================
# CREAR BOT
# ============================================================

bot = MiBot()

# ============================================================
# COMANDO /TEST
# ============================================================

@bot.tree.command(
    name="test",
    description="Comprueba si el bot responde."
)
async def test(
    interaction: discord.Interaction
):

    print("")
    print("=" * 70)
    print("🟢 /TEST RECIBIDO")
    print("=" * 70)

    print(
        f"👤 Usuario: {interaction.user}"
    )

    print(
        f"🏠 Servidor: {interaction.guild}"
    )

    print(
        f"🆔 Guild ID: {interaction.guild_id}"
    )

    try:

        await interaction.response.send_message(
            "✅ ¡El bot responde correctamente!"
        )

        print(
            "✅ /TEST RESPONDIDO"
        )

    except Exception as error:

        print(
            f"❌ Error /test: "
            f"{type(error).__name__}: {error}"
        )

# ============================================================
# COMANDO !TEST
# ============================================================

@bot.command(
    name="test"
)
async def test_prefix(
    ctx: commands.Context
):

    print(
        f"🟢 !test recibido de {ctx.author}"
    )

    await ctx.send(
        "✅ ¡El comando `!test` funciona correctamente!"
    )

# ============================================================
# EVENTO CONNECT
# ============================================================

@bot.event
async def on_connect():

    print(
        "🟡 Bot conectado al Gateway de Discord."
    )

# ============================================================
# EVENTO READY
# ============================================================

@bot.event
async def on_ready():

    print("")
    print("=" * 70)
    print("🟢 BOT READY")
    print("=" * 70)

    print(
        f"🤖 Bot: {bot.user}"
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
        f"📊 Estado: {bot.status}"
    )

    print("")
    print(
        f"📦 Cogs cargados: "
        f"{len(bot.cogs)}"
    )

    print(
        "⌨️ Prefix: !"
    )

    print(
        "⚡ Slash: /"
    )

    print("=" * 70)

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
            "❌ Te faltan argumentos.",
            delete_after=8
        )

        return

    print("")
    print("=" * 70)
    print("❌ ERROR EN PREFIX COMMAND")
    print("=" * 70)

    print(
        f"Tipo: {type(error).__name__}"
    )

    print(
        f"Error: {error}"
    )

    traceback.print_exception(
        type(error),
        error,
        error.__traceback__
    )

    print("=" * 70)

# ============================================================
# ERROR SLASH
# ============================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: discord.app_commands.AppCommandError
):

    print("")
    print("=" * 70)
    print("❌ ERROR EN SLASH COMMAND")
    print("=" * 70)

    print(
        f"Tipo: {type(error).__name__}"
    )

    print(
        f"Error: {error}"
    )

    traceback.print_exception(
        type(error),
        error,
        error.__traceback__
    )

    print("=" * 70)

    try:

        message = (
            "❌ Ocurrió un error "
            "ejecutando el comando."
        )

        if interaction.response.is_done():

            await interaction.followup.send(
                message,
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                message,
                ephemeral=True
            )

    except Exception as send_error:

        print(
            f"❌ No pude enviar el error: "
            f"{send_error}"
        )

# ============================================================
# DASHBOARD HELPERS
# ============================================================

def is_logged_in():

    return "user" in session

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
# DASHBOARD HOME
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

    session["oauth_state"] = state

    params = {
        "client_id": DISCORD_CLIENT_ID,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds",
        "state": state
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
# OAUTH CALLBACK
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

    if not state or state != saved_state:

        return (
            "<h1>Error de seguridad</h1>"
            "<p>El estado OAuth2 no coincide.</p>",
            400
        )

    session.pop(
        "oauth_state",
        None
    )

    token_data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI
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
            f"❌ OAuth error: {error}"
        )

        return (
            "<h1>Error de conexión</h1>",
            500
        )

    if token_response.status_code != 200:

        print(
            "❌ Discord OAuth:",
            token_response.text
        )

        return (
            "<h1>Error de autenticación</h1>",
            400
        )

    token_json = token_response.json()

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        return (
            "<h1>Error</h1>"
            "<p>No se recibió Access Token.</p>",
            400
        )

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
            f"❌ Error usuario: {error}"
        )

        return (
            "<h1>Error obteniendo usuario</h1>",
            500
        )

    if user_response.status_code != 200:

        return (
            "<h1>No se pudo verificar "
            "tu cuenta.</h1>",
            400
        )

    user = user_response.json()

    session["user"] = {
        "id": user.get("id"),
        "username": user.get("username"),
        "global_name": user.get("global_name"),
        "avatar": user.get("avatar")
    }

    session["access_token"] = access_token

    print(
        f"✅ Login: {user.get('username')}"
    )

    return redirect("/")

# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    username = None

    if "user" in session:

        username = session["user"].get(
            "username"
        )

    session.clear()

    print(
        f"👋 Logout: {username}"
    )

    return redirect("/")

# ============================================================
# API ME
# ============================================================

@app.route("/api/me")
def api_me():

    user = session.get(
        "user"
    )

    if not user:

        return jsonify({
            "logged_in": False,
            "user": None
        })

    return jsonify({
        "logged_in": True,
        "user": user
    })

# ============================================================
# API STATUS
# ============================================================

@app.route("/api/status")
def api_status():

    if bot.is_ready():

        return jsonify({
            "online": True,
            "bot": str(bot.user),
            "bot_id": bot.user.id,
            "guilds": len(bot.guilds),
            "latency": round(
                bot.latency * 1000
            ),
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
# API GUILDS
# ============================================================

@app.route("/api/guilds")
def api_guilds():

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message":
                "Debes iniciar sesión con Discord.",
            "guilds": []
        }), 401

    if not bot.is_ready():

        return jsonify({
            "success": False,
            "message":
                "El bot todavía no está listo.",
            "guilds": []
        }), 503

    guilds = []

    for guild in bot.guilds:

        guilds.append({
            "id": guild.id,
            "name": guild.name,
            "member_count":
                guild.member_count,
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
# API GUILD
# ============================================================

@app.route(
    "/api/guild/<int:guild_id>"
)
def api_guild(guild_id):

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message":
                "Debes iniciar sesión con Discord."
        }), 401

    if not bot.is_ready():

        return jsonify({
            "success": False,
            "message":
                "El bot todavía no está listo."
        }), 503

    guild = bot.get_guild(
        guild_id
    )

    if guild is None:

        return jsonify({
            "success": False,
            "message":
                "El bot no está en este servidor."
        }), 404

    return jsonify({
        "success": True,
        "guild": {
            "id": guild.id,
            "name": guild.name,
            "member_count":
                guild.member_count,
            "channel_count":
                len(guild.channels),
            "role_count":
                len(guild.roles),
            "icon": (
                str(guild.icon.url)
                if guild.icon
                else None
            )
        }
    })

# ============================================================
# API SECURITY
# ============================================================

@app.route(
    "/api/security/<int:guild_id>",
    methods=["GET"]
)
def api_security(guild_id):

    if not is_logged_in():

        return jsonify({
            "success": False,
            "message":
                "Debes iniciar sesión."
        }), 401

    guild = bot.get_guild(
        guild_id
    )

    if guild is None:

        return jsonify({
            "success": False,
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
            "success": False,
            "message":
                "No perteneces al servidor."
        }), 403

    if not (
        member.guild_permissions.manage_guild
        or
        member.guild_permissions.administrator
    ):

        return jsonify({
            "success": False,
            "message":
                "No tienes permisos."
        }), 403

    antispam = bot.get_cog(
        "AntiSpam"
    )

    antiflood = bot.get_cog(
        "AntiFlood"
    )

    antilink = bot.get_cog(
        "AntiLink"
    )

    return jsonify({
        "success": True,
        "security": {
            "antispam": bool(antispam),
            "antiflood": bool(antiflood),
            "antilink": bool(antilink)
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
            "success": False,
            "message":
                "Debes iniciar sesión."
        }), 401

    guild = bot.get_guild(
        guild_id
    )

    if guild is None:

        return jsonify({
            "success": False,
            "message":
                "Servidor no encontrado."
        }), 404

    user_id = int(
        session["user"]["id"]
    )

    member = guild.get_member(
        user_id
    )

    if member is None:

        return jsonify({
            "success": False,
            "message":
                "No perteneces al servidor."
        }), 403

    if not (
        member.guild_permissions.manage_guild
        or
        member.guild_permissions.administrator
    ):

        return jsonify({
            "success": False,
            "message":
                "No tienes permisos."
        }), 403

    data = request.get_json(
        silent=True
    )

    if not data:

        return jsonify({
            "success": False,
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
            "success": False,
            "message":
                "enabled debe ser true o false."
        }), 400

    cog_names = {
        "antispam": "AntiSpam",
        "antiflood": "AntiFlood",
        "antilink": "AntiLink"
    }

    cog_name = cog_names.get(
        security_type
    )

    if not cog_name:

        return jsonify({
            "success": False,
            "message":
                "Sistema desconocido."
        }), 400

    cog = bot.get_cog(
        cog_name
    )

    if cog is None:

        return jsonify({
            "success": False,
            "message":
                "El sistema no está cargado."
        }), 500

    if not hasattr(
        cog,
        "config"
    ):

        return jsonify({
            "success": False,
            "message":
                "El sistema no tiene "
                "configuración compatible."
        }), 500

    cog.config[guild_id] = enabled

    print(
        f"🛡️ {security_type.upper()} "
        f"en {guild.name}: "
        f"{'ACTIVADO' if enabled else 'DESACTIVADO'}"
    )

    return jsonify({
        "success": True,
        "type": security_type,
        "guild_id": guild_id,
        "enabled": enabled
    })

# ============================================================
# SECURITY ROUTES
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
        f"🌐 Flask iniciado "
        f"en puerto {PORT}"
    )

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False,
        threaded=True
    )

# ============================================================
# MAIN
# ============================================================

async def main():

    print("")
    print("=" * 70)
    print("🚀 INICIANDO BOT")
    print("=" * 70)

    if not TOKEN:

        print(
            "❌ FALTA DISCORD_TOKEN"
        )

        return

    print(
        "🔑 DISCORD_TOKEN encontrado."
    )

    print(
        f"📦 discord.py: "
        f"{discord.__version__}"
    )

    print(
        f"🏠 Guild principal: "
        f"{GUILD_ID}"
    )

    # ========================================================
    # FLASK
    # ========================================================

    try:

        web_thread = threading.Thread(
            target=run_web,
            daemon=True
        )

        web_thread.start()

        print(
            "✅ Dashboard iniciado."
        )

    except Exception as error:

        print(
            f"❌ Error Flask: "
            f"{error}"
        )

    # ========================================================
    # DISCORD
    # ========================================================

    try:

        print("")
        print(
            "🔵 Conectando a Discord..."
        )

        await bot.start(
            TOKEN
        )

    except discord.LoginFailure:

        print("")
        print("=" * 70)
        print("❌ TOKEN INVÁLIDO")
        print("=" * 70)

        print(
            "Revisá DISCORD_TOKEN en Render."
        )

    except discord.PrivilegedIntentsRequired as error:

        print("")
        print("=" * 70)
        print("❌ PRIVILEGED INTENTS")
        print("=" * 70)

        print(
            "Activá Message Content Intent "
            "y Server Members Intent "
            "en Discord Developer Portal."
        )

        print(
            f"Detalles: {error}"
        )

    except discord.HTTPException as error:

        print("")
        print("=" * 70)
        print("❌ ERROR HTTP DISCORD")
        print("=" * 70)

        print(
            f"Status: {error.status}"
        )

        print(
            f"Detalles: {error}"
        )

    except Exception as error:

        print("")
        print("=" * 70)
        print("❌ ERROR FATAL")
        print("=" * 70)

        print(
            f"Tipo: {type(error).__name__}"
        )

        print(
            f"Error: {error}"
        )

        traceback.print_exc()

    finally:

        print("")
        print("=" * 70)
        print("🛑 BOT FINALIZADO")
        print("=" * 70)

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

    except Exception as error:

        print(
            f"❌ Error fuera de main: "
            f"{error}"
        )

        traceback.print_exc()