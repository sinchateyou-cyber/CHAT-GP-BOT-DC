import os
import asyncio
import threading
import secrets
import traceback
from urllib.parse import urlencode

import discord
from discord.ext import commands
from discord import app_commands

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

# ============================================================
# LÍMITES
# ============================================================

# Discord permite como máximo 100 application commands
# globales por aplicación.
MAX_GLOBAL_SLASH_COMMANDS = 100


# ============================================================
# TU SERVIDOR
# ============================================================

GUILD_ID = 1534290216418938891

GUILD_OBJECT = discord.Object(
    id=GUILD_ID
)


# ============================================================
# SESSION SECRET
# ============================================================

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
# DISCORD OAUTH
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
# COMMAND TREE LIMITADO
# ============================================================

class LimitedCommandTree(app_commands.CommandTree):
    """
    CommandTree que evita que el bot explote cuando llega
    al límite de 100 slash commands globales.

    Los comandos que superen el límite quedan disponibles
    mediante el prefijo, pero no como slash command.
    """

    def __init__(self, bot):
        super().__init__(bot)

        self.skipped_commands = []

    def add_command(
        self,
        command,
        /,
        *,
        guild=None,
        guilds=None,
        override=False
    ):
        """
        Agrega comandos al árbol.

        Si es un comando GLOBAL y ya tenemos 100,
        no lo agregamos al árbol.

        De esta manera el HybridCommand sigue siendo
        un comando de prefijo.
        """

        # ----------------------------------------------------
        # COMANDO DE SERVIDOR
        # ----------------------------------------------------

        if guild is not None or guilds is not None:

            return super().add_command(
                command,
                guild=guild,
                guilds=guilds,
                override=override
            )

        # ----------------------------------------------------
        # COMANDO GLOBAL
        # ----------------------------------------------------

        current_commands = self.get_commands()

        # Evitar duplicados
        existing_names = {
            cmd.name
            for cmd in current_commands
        }

        if command.name in existing_names and not override:

            return super().add_command(
                command,
                guild=guild,
                guilds=guilds,
                override=override
            )

        # ----------------------------------------------------
        # LÍMITE
        # ----------------------------------------------------

        if len(current_commands) >= MAX_GLOBAL_SLASH_COMMANDS:

            command_name = getattr(
                command,
                "name",
                "desconocido"
            )

            if command_name not in self.skipped_commands:

                self.skipped_commands.append(
                    command_name
                )

                print(
                    f"⚠️ LÍMITE SLASH ALCANZADO: "
                    f"/{command_name}"
                )

                print(
                    "   ↳ Disponible por prefijo."
                )

            # IMPORTANTE:
            # No agregamos el app command al árbol.
            return

        # ----------------------------------------------------
        # AGREGAR NORMALMENTE
        # ----------------------------------------------------

        return super().add_command(
            command,
            guild=guild,
            guilds=guilds,
            override=override
        )


# ============================================================
# BOT
# ============================================================

class MiBot(commands.Bot):

    def __init__(self):

        super().__init__(
            command_prefix="s",
            intents=intents,
            help_command=None,
            tree_cls=LimitedCommandTree
        )

        # ----------------------------------------------------
        # ESTADO
        # ----------------------------------------------------

        self.cogs_loaded = []
        self.cogs_failed = []

        self.synced = False
        self.sync_count = 0

        self.prefix_only_commands = []

        self.setup_finished = False

    # ========================================================
    # SETUP HOOK
    # ========================================================

    async def setup_hook(self):

        print("")
        print("=" * 70)
        print("📦 INICIANDO SETUP DEL BOT")
        print("=" * 70)

        # ----------------------------------------------------
        # CARGAR COGS
        # ----------------------------------------------------

        await self.load_all_cogs()

        # ----------------------------------------------------
        # CARGAR VIEWS
        # ----------------------------------------------------

        await self.load_persistent_views()

        # ----------------------------------------------------
        # COMANDO TEST
        # ----------------------------------------------------

        self.add_test_command()

        # ----------------------------------------------------
        # MOSTRAR COMANDOS
        # ----------------------------------------------------

        await self.show_loaded_commands()

        # ----------------------------------------------------
        # SINCRONIZAR
        # ----------------------------------------------------

        await self.sync_commands()

        self.setup_finished = True

        print("")
        print("=" * 70)
        print("✅ SETUP COMPLETADO")
        print("=" * 70)

    # ========================================================
    # CARGAR COGS
    # ========================================================

    async def load_all_cogs(self):

        extensions = [

            # =================================================
            # MODERACIÓN
            # =================================================

            "cogs.lock",
            "cogs.borrarcanales",
            "cogs.casamiento",
            "cogs.botinvite",
            "cogs.vcstats",
            "cogs.copy",
            "cogs.clear",
            "cogs.instagram",
            "cogs.pinterest",
            "cogs.gif",
            "cogs.eco",
            "cogs.gifcopy",
            "cogs.canalpermitido",
            "cogs.bienvenida",
            "cogs.stats",
            "cogs.estado_space",
            "cogs.jail",

            # =================================================
            # SEGURIDAD
            # =================================================

            "cogs.md",
            "cogs.invitacion",
            "cogs.valenolleka",
            "cogs.estado_space",

            # =================================================
            # UTILIDADES
            # =================================================

            "cogs.avatar",
            "cogs.nick",

            # =================================================
            # ROLES
            # =================================================

            "cogs.addrole",
            "cogs.createrole",
            "cogs.deleterole",
            "cogs.role_permissions",
            "cogs.reactionroles",
            "cogs.customroles",

            # =================================================
            # ALIANZAS
            # =================================================

            "cogs.alliances",
            "cogs.permisos_alianza",
            "cogs.canal_confesiones",
            "cogs.privatechannel",
            "cogs.imagenes",

            # =================================================
            # CANALES / SERVIDOR
            # =================================================

            "cogs.canales",
            "cogs.logs",
            "cogs.server_setup",
            "cogs.reglas",
            "cogs.confesiones",

            # =================================================
            # AYUDA / OWNER
            # =================================================

            "cogs.help",
            "cogs.owner",

            # =================================================
            # INVITACIONES
            # =================================================

            "cogs.invite",
            "cogs.invites",
            "cogs.invites_command",
            "cogs.invites_leaderboard",

            # =================================================
            # BOT
            # =================================================

            "cogs.botinfo",
            "cogs.config",
            "cogs.addemoji",
            "cogs.status",

            # =================================================
            # OTROS
            # =================================================

            "cogs.spotify",

            # =================================================
            # ECONOMÍA
            # =================================================

            "cogs.economia",
            "cogs.apuestas",
            "cogs.addmoney",

            # =================================================
            # VOICE
            # =================================================

            "cogs.voice_creator",
            "cogs.voice_actions",

            # =================================================
            # MEDIA ROLE
            # =================================================

            "cogs.media_rol",

            # =================================================
            # REACTION ROLES
            # =================================================

            "cogs.iconrol",

            # =================================================
            # OTROS SISTEMAS
            # =================================================

            "cogs.robo",
            "cogs.aliases",
            "cogs.clonador",

            # =================================================
            # TICKETS
            # =================================================

            "cogs.tickets",

        ]

        print("")
        print("=" * 70)
        print("📦 CARGANDO COGS")
        print("=" * 70)

        for extension in extensions:

            try:

                await self.load_extension(
                    extension
                )

                self.cogs_loaded.append(
                    extension
                )

                print(
                    f"✅ CARGADO: {extension}"
                )

            except commands.ExtensionAlreadyLoaded:

                print(
                    f"⚠️ YA CARGADO: {extension}"
                )

            except commands.ExtensionNotFound:

                self.cogs_failed.append(
                    (
                        extension,
                        "No encontrado"
                    )
                )

                print(
                    f"⚠️ NO ENCONTRADO: {extension}"
                )

            except Exception as error:

                self.cogs_failed.append(
                    (
                        extension,
                        error
                    )
                )

                print("")
                print(
                    f"❌ ERROR CARGANDO: {extension}"
                )

                print(
                    f"   Tipo: {type(error).__name__}"
                )

                print(
                    f"   Detalle: {error}"
                )

                traceback.print_exc()

        # ----------------------------------------------------
        # ESTADÍSTICAS
        # ----------------------------------------------------

        slash_count = len(
            self.tree.get_commands()
        )

        skipped_count = len(
            getattr(
                self.tree,
                "skipped_commands",
                []
            )
        )

        print("")
        print("=" * 70)

        print(
            f"📦 COGS CARGADOS: "
            f"{len(self.cogs_loaded)}"
        )

        print(
            f"❌ COGS CON ERROR: "
            f"{len(self.cogs_failed)}"
        )

        print(
            f"⚡ SLASH GLOBALES: "
            f"{slash_count}/{MAX_GLOBAL_SLASH_COMMANDS}"
        )

        print(
            f"⌨️ COMANDOS FUERA DEL SLASH: "
            f"{skipped_count}"
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

        # ----------------------------------------------------
        # TICKETS
        # ----------------------------------------------------

        try:

            from cogs.tickets import (
                TicketView,
                CloseTicketView
            )

            self.add_view(
                TicketView()
            )

            print(
                "✅ TicketView registrada"
            )

            self.add_view(
                CloseTicketView()
            )

            print(
                "✅ CloseTicketView registrada"
            )

        except Exception as error:

            print(
                "⚠️ Ticket Views no disponibles:"
            )

            print(
                f"   {type(error).__name__}: {error}"
            )

        # ----------------------------------------------------
        # MEDIA ROLE
        # ----------------------------------------------------

        try:

            from cogs.media_rol import MediaRoleView

            self.add_view(
                MediaRoleView()
            )

            print(
                "✅ MediaRoleView registrada"
            )

        except Exception as error:

            print(
                "⚠️ MediaRoleView no disponible:"
            )

            print(
                f"   {type(error).__name__}: {error}"
            )

        print("")
        print("=" * 70)
        print("🎭 VIEWS PERSISTENTES CARGADAS")
        print("=" * 70)

    # ========================================================
    # COMANDO TEST
    # ========================================================

    def add_test_command(self):

        if self.get_command(
            "test"
        ) is not None:

            return

        @self.command(
            name="test"
        )
        async def test(
            ctx: commands.Context
        ):

            print(
                f"🟢 TEST RECIBIDO DE {ctx.author}"
            )

            await ctx.send(
                "✅ ¡El bot responde correctamente!"
            )

        print(
            "✅ Comando stest registrado"
        )

    # ========================================================
    # MOSTRAR COMANDOS
    # ========================================================

    async def show_loaded_commands(self):

        print("")
        print("=" * 70)
        print("📋 COMANDOS CARGADOS")
        print("=" * 70)

        # ----------------------------------------------------
        # PREFIX
        # ----------------------------------------------------

        prefix_commands = [
            command
            for command in self.commands
            if not command.hidden
        ]

        print("")
        print(
            f"⌨️ COMANDOS PREFIX: "
            f"{len(prefix_commands)}"
        )

        for command in sorted(
            prefix_commands,
            key=lambda x: x.name
        ):

            print(
                f"   s{command.name}"
            )

        # ----------------------------------------------------
        # SLASH GLOBAL
        # ----------------------------------------------------

        global_commands = self.tree.get_commands()

        print("")
        print(
            f"🌎 SLASH GLOBAL: "
            f"{len(global_commands)}/"
            f"{MAX_GLOBAL_SLASH_COMMANDS}"
        )

        for command in sorted(
            global_commands,
            key=lambda x: x.name
        ):

            print(
                f"   ⚡ /{command.name}"
            )

        # ----------------------------------------------------
        # SLASH SERVIDOR
        # ----------------------------------------------------

        guild_commands = self.tree.get_commands(
            guild=GUILD_OBJECT
        )

        print("")
        print(
            f"🏠 SLASH DEL SERVIDOR PRE-SYNC: "
            f"{len(guild_commands)}"
        )

        for command in sorted(
            guild_commands,
            key=lambda x: x.name
        ):

            print(
                f"   🏠 /{command.name}"
            )

        # ----------------------------------------------------
        # OMITIDOS
        # ----------------------------------------------------

        skipped = getattr(
            self.tree,
            "skipped_commands",
            []
        )

        print("")

        if skipped:

            print(
                f"⚠️ COMANDOS SLASH OMITIDOS: "
                f"{len(skipped)}"
            )

            for name in skipped:

                print(
                    f"   ⌨️ s{name}"
                )

        else:

            print(
                "✅ No hay comandos omitidos."
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

            # ------------------------------------------------
            # LIMPIAR COMANDOS DEL SERVIDOR
            # ------------------------------------------------
            #
            # Primero limpiamos la copia local del servidor
            # para evitar comandos viejos.
            # ------------------------------------------------

            try:

                self.tree.clear_commands(
                    guild=GUILD_OBJECT
                )

                print(
                    "🧹 Comandos antiguos del servidor limpiados."
                )

            except Exception as error:

                print(
                    "⚠️ No se pudieron limpiar "
                    "comandos anteriores:"
                )

                print(
                    f"   {type(error).__name__}: {error}"
                )

            # ------------------------------------------------
            # COPIAR GLOBALES AL SERVIDOR
            # ------------------------------------------------

            self.tree.copy_global_to(
                guild=GUILD_OBJECT
            )

            print(
                "📋 Comandos disponibles copiados al servidor."
            )

            # ------------------------------------------------
            # SYNC DIRECTO AL SERVIDOR
            # ------------------------------------------------

            synced = await self.tree.sync(
                guild=GUILD_OBJECT
            )

            self.synced = True

            self.sync_count = len(
                synced
            )

            print("")
            print(
                f"✅ {len(synced)} SLASH COMMANDS "
                f"SINCRONIZADOS"
            )

            print(
                f"🏠 SERVIDOR: {GUILD_ID}"
            )

            # ------------------------------------------------
            # LISTAR
            # ------------------------------------------------

            alliance_commands = []

            print("")

            for command in sorted(
                synced,
                key=lambda x: x.name
            ):

                print(
                    f"   ⚡ /{command.name}"
                )

                if command.name in (
                    "alianza",
                    "alianzas",
                    "configalianzas"
                ):

                    alliance_commands.append(
                        command.name
                    )

            # ------------------------------------------------
            # ALIANZAS
            # ------------------------------------------------

            print("")
            print(
                "🤝 COMPROBANDO SISTEMA DE ALIANZAS..."
            )

            required_alliance_commands = {
                "alianza",
                "alianzas",
                "configalianzas"
            }

            found_alliance_commands = set(
                alliance_commands
            )

            missing = (
                required_alliance_commands
                - found_alliance_commands
            )

            if not missing:

                print(
                    "✅ SISTEMA DE ALIANZAS COMPLETO"
                )

                print(
                    "   ⚡ /alianza"
                )

                print(
                    "   ⚡ /alianzas"
                )

                print(
                    "   ⚡ /configalianzas"
                )

            else:

                print(
                    "⚠️ FALTAN COMANDOS DE ALIANZAS:"
                )

                for command_name in sorted(
                    missing
                ):

                    print(
                        f"   ❌ /{command_name}"
                    )

                if "cogs.alliances" in self.cogs_loaded:

                    print(
                        "ℹ️ cogs.alliances fue cargado, "
                        "pero esos comandos no están "
                        "entre los slash sincronizados."
                    )

                else:

                    print(
                        "❌ cogs.alliances NO fue cargado."
                    )

            # ------------------------------------------------
            # ESTADÍSTICAS
            # ------------------------------------------------

            print("")
            print(
                "📊 RESUMEN SLASH"
            )

            print(
                f"   Globales disponibles: "
                f"{len(self.tree.get_commands())}/"
                f"{MAX_GLOBAL_SLASH_COMMANDS}"
            )

            print(
                f"   Sincronizados en servidor: "
                f"{self.sync_count}"
            )

            skipped = getattr(
                self.tree,
                "skipped_commands",
                []
            )

            print(
                f"   Solo prefijo: "
                f"{len(skipped)}"
            )

            if skipped:

                print("")
                print(
                    "⌨️ COMANDOS QUE FUNCIONAN "
                    "SOLO CON PREFIJO:"
                )

                for name in skipped:

                    print(
                        f"   s{name}"
                    )

        except discord.HTTPException as error:

            print("")
            print(
                "❌ DISCORD RECHAZÓ "
                "LA SINCRONIZACIÓN"
            )

            print(
                f"   Status: {error.status}"
            )

            print(
                f"   Detalle: {error}"
            )

            traceback.print_exc()

        except Exception as error:

            print("")
            print(
                "❌ ERROR SINCRONIZANDO"
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
        print("🌎 SYNC COMPLETADO")
        print("=" * 70)


# ============================================================
# CREAR BOT
# ============================================================

bot = MiBot()


# ============================================================
# ON CONNECT
# ============================================================

@bot.event
async def on_connect():

    print(
        "🟡 Bot conectado al Gateway de Discord."
    )


# ============================================================
# ON READY
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
        f"🌐 Servidores: "
        f"{len(bot.guilds)}"
    )

    print(
        f"📡 Latencia: "
        f"{round(bot.latency * 1000)} ms"
    )

    print(
        f"📦 Cogs cargados: "
        f"{len(bot.cogs)}"
    )

    print(
        f"⌨️ Comandos prefix: "
        f"{len(bot.commands)}"
    )

    print(
        f"⚡ Slash disponibles: "
        f"{len(bot.tree.get_commands())}/"
        f"{MAX_GLOBAL_SLASH_COMMANDS}"
    )

    print(
        f"⚡ Slash sincronizados: "
        f"{bot.sync_count}"
    )

    skipped = getattr(
        bot.tree,
        "skipped_commands",
        []
    )

    print(
        f"⌨️ Solo prefix por límite: "
        f"{len(skipped)}"
    )

    # --------------------------------------------------------
    # ALIANZAS
    # --------------------------------------------------------

    alliances_cog = bot.get_cog(
        "Alliances"
    )

    if alliances_cog:

        print(
            "🤝 Alliances: ✅ CARGADO"
        )

    else:

        print(
            "🤝 Alliances: ❌ NO CARGADO"
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

    if isinstance(
        error,
        commands.CommandOnCooldown
    ):

        await ctx.send(
            f"⏳ Esperá "
            f"**{error.retry_after:.1f}s**.",
            delete_after=8
        )

        return

    print(
        f"❌ ERROR PREFIX: "
        f"{type(error).__name__}: {error}"
    )

    traceback.print_exception(
        type(error),
        error,
        error.__traceback__
    )


# ============================================================
# ERROR SLASH
# ============================================================

@bot.tree.error
async def on_app_command_error(
    interaction: discord.Interaction,
    error: discord.app_commands.AppCommandError
):

    print(
        f"❌ ERROR SLASH: "
        f"{type(error).__name__}: {error}"
    )

    traceback.print_exception(
        type(error),
        error,
        error.__traceback__
    )

    try:

        mensaje = (
            "❌ Ocurrió un error "
            "ejecutando el comando."
        )

        if interaction.response.is_done():

            await interaction.followup.send(
                mensaje,
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                mensaje,
                ephemeral=True
            )

    except Exception:

        pass


# ============================================================
# DASHBOARD
# ============================================================

def is_logged_in():

    return "user" in session


# ============================================================
# HOME
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
# OAUTH CALLBACK
# ============================================================

@app.route("/auth/callback")
def oauth_callback():

    error = request.args.get(
        "error"
    )

    if error:

        return (
            f"<h1>Login cancelado</h1>"
            f"<p>{error}</p>"
            f"<a href='/'>Volver</a>",
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
            "<p>El estado OAuth2 "
            "no coincide.</p>",
            400
        )

    session.pop(
        "oauth_state",
        None
    )

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

    token_json = (
        token_response.json()
    )

    access_token = token_json.get(
        "access_token"
    )

    if not access_token:

        return (
            "<h1>Error</h1>"
            "<p>No se recibió "
            "Access Token.</p>",
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

    except requests.RequestException:

        return (
            "<h1>Error obteniendo "
            "usuario</h1>",
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

        "id":
            user.get("id"),

        "username":
            user.get("username"),

        "global_name":
            user.get("global_name"),

        "avatar":
            user.get("avatar")
    }

    session["access_token"] = (
        access_token
    )

    return redirect(
        "/"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        "/"
    )


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
# API STATUS
# ============================================================

@app.route("/api/status")
def api_status():

    if bot.is_ready():

        skipped = getattr(
            bot.tree,
            "skipped_commands",
            []
        )

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
                str(bot.status),

            "slash_synced":
                bot.synced,

            "slash_count":
                bot.sync_count,

            "slash_global_count":
                len(
                    bot.tree.get_commands()
                ),

            "slash_limit":
                MAX_GLOBAL_SLASH_COMMANDS,

            "prefix_only_count":
                len(skipped)
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
            "offline",

        "slash_synced":
            False,

        "slash_count":
            0,

        "slash_global_count":
            0,

        "slash_limit":
            MAX_GLOBAL_SLASH_COMMANDS,

        "prefix_only_count":
            0
    })


# ============================================================
# API GUILDS
# ============================================================

@app.route("/api/guilds")
def api_guilds():

    if not is_logged_in():

        return jsonify({

            "success":
                False,

            "message":
                "Debes iniciar sesión "
                "con Discord.",

            "guilds":
                []
        }), 401

    if not bot.is_ready():

        return jsonify({

            "success":
                False,

            "message":
                "El bot todavía "
                "no está listo.",

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

            "icon":
                (
                    str(guild.icon.url)
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
# API GUILD
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
                "El bot no está "
                "en este servidor."
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

            "icon":
                (
                    str(guild.icon.url)
                    if guild.icon
                    else None
                )
        }
    })


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
        "🔑 TOKEN ENCONTRADO"
    )

    print(
        f"📦 discord.py: "
        f"{discord.__version__}"
    )

    # --------------------------------------------------------
    # FLASK
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DISCORD
    # --------------------------------------------------------

    try:

        print(
            "🔵 CONECTANDO A DISCORD..."
        )

        await bot.start(
            TOKEN
        )

    except discord.LoginFailure:

        print(
            "❌ TOKEN INVÁLIDO"
        )

    except discord.PrivilegedIntentsRequired as error:

        print(
            "❌ ACTIVÁ LOS INTENTS "
            "PRIVILEGIADOS EN EL PORTAL "
            "DE DISCORD."
        )

        print(
            error
        )

    except Exception as error:

        print(
            f"❌ ERROR FATAL: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        traceback.print_exc()

    finally:

        print(
            "🛑 BOT FINALIZADO"
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

    except Exception as error:

        print(
            f"❌ ERROR FUERA DE MAIN: "
            f"{type(error).__name__}: {error}"
        )

        traceback.print_exc()