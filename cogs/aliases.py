import discord
from discord.ext import commands


# ============================================================
# ALIASES GLOBALES
# ============================================================

ALIASES = {

    # ==========================
    # ECONOMÍA
    # ==========================

    "balance": [
        "bal",
        "money",
        "saldo",
    ],

    "daily": [
        "d",
    ],

    "work": [
        "w",
        "trabajo",
    ],

    "pay": [
        "p",
        "pagar",
    ],

    "coinflip": [
        "cf",
        "coin",
    ],

    "dice": [
        "dado",
    ],

    "slots": [
        "slot",
        "tragamonedas",
    ],

    "guess": [
        "g",
        "adivinar",
    ],

    "leaderboard": [
        "lb",
        "top",
        "ranking",
    ],

    "economia": [
        "eco",
    ],

    # ==========================
    # ROBOS
    # ==========================

    "robar": [
        "robo",
        "rob",
    ],

    "robostats": [
        "rs",
        "robstats",
    ],

    "ayudarobo": [
        "ar",
    ],

    # ==========================
    # ACCIONES
    # ==========================

    "hug": [
        "abrazo",
    ],

    "kiss": [
        "beso",
    ],

    "slap": [
        "cachetada",
    ],

    "pat": [
        "mimitos",
    ],

    "cuddle": [
        "acurrucar",
    ],

    "love": [
        "amor",
    ],

    "punch": [
        "golpear",
    ],

    "bite": [
        "morder",
    ],

    "highfive": [
        "chocar",
        "hf",
    ],

    "wave": [
        "saludar",
    ],

    # ==========================
    # USUARIOS
    # ==========================

    "avatar": [
        "av",
        "foto",
        "pfp",
    ],

    "userinfo": [
        "ui",
        "user",
        "usuario",
    ],

    "nick": [
        "nickname",
    ],

    "afk": [
        "away",
    ],

    # ==========================
    # MODERACIÓN
    # ==========================

    "ban": [
        "b",
    ],

    "kick": [
        "k",
        "expulsar",
    ],

    "timeout": [
        "to",
        "mute",
    ],

    "untimeout": [
        "unto",
        "unmute",
    ],

    "clear": [
        "c",
        "purge",
        "limpiar",
    ],

    "lock": [
        "cerrar",
    ],

    "unlock": [
        "abrir",
    ],

    # ==========================
    # INVITACIONES
    # ==========================

    "invite": [
        "inv",
    ],

    "invites": [
        "invs",
    ],

    "invitesleaderboard": [
        "ilb",
        "invlb",
    ],

    # ==========================
    # BOT
    # ==========================

    "help": [
        "h",
        "ayuda",
    ],

    "botinfo": [
        "bi",
        "bot",
    ],

    "test": [
        "t",
    ],

    # ==========================
    # UTILIDADES
    # ==========================

    "ping": [
        "pong",
    ],

    "say": [
        "decir",
    ],

    "addemoji": [
        "emoji",
        "em",
    ],

    # ==========================
    # ROLES
    # ==========================

    "addrole": [
        "arole",
    ],

    "createrole": [
        "cr",
        "crearrol",
    ],

    "deleterole": [
        "dr",
        "borrarrol",
    ],

    # ==========================
    # TICKETS
    # ==========================

    "ticket": [
        "tkt",
    ],

    "closeticket": [
        "ct",
        "cerrarticket",
    ],

    # ==========================
    # SERVIDOR
    # ==========================

    "server": [
        "sv",
        "servidor",
    ],

    "setbienvenida": [
        "bienvenida",
        "setwelcome",
    ],

    # ==========================
    # MÚSICA
    # ==========================

    "play": [
        "reproducir",
    ],

    "pause": [
        "pa",
    ],

    "resume": [
        "continuar",
    ],

    "skip": [
        "saltar",
    ],

    "stop": [
        "st",
        "parar",
    ],

    "queue": [
        "q",
        "cola",
    ],

    "volume": [
        "vol",
    ],

    "leave": [
        "dc",
        "disconnect",
    ],
}


# ============================================================
# COG
# ============================================================

class Aliases(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.registered = []

        self.skipped = []

    # ========================================================
    # CARGAR
    # ========================================================

    async def cog_load(self):

        await self.register_aliases()

    # ========================================================
    # REGISTRAR ALIASES
    # ========================================================

    async def register_aliases(self):

        print("")
        print("=" * 60)
        print("[ALIASES] REGISTRANDO ALIASES")
        print("=" * 60)

        for command_name, aliases in ALIASES.items():

            # ------------------------------------------------
            # BUSCAR COMANDO
            # ------------------------------------------------

            command = self.bot.get_command(
                command_name
            )

            if command is None:

                print(
                    f"[ALIASES] ⚠️ "
                    f"No existe: {command_name}"
                )

                continue

            # ------------------------------------------------
            # SOLO COMANDOS PREFIX
            # ------------------------------------------------

            if not isinstance(
                command,
                commands.Command
            ):

                print(
                    f"[ALIASES] ⚠️ "
                    f"{command_name} no es "
                    f"un comando de prefijo compatible."
                )

                continue

            # ------------------------------------------------
            # ALIASES
            # ------------------------------------------------

            for alias in aliases:

                alias = alias.lower().strip()

                if not alias:
                    continue

                # --------------------------------------------
                # MISMO NOMBRE
                # --------------------------------------------

                if alias == command.name.lower():

                    continue

                # --------------------------------------------
                # YA EXISTE
                # --------------------------------------------

                existing = self.bot.get_command(
                    alias
                )

                if existing is not None:

                    print(
                        f"[ALIASES] ⚠️ "
                        f"{alias} ya está ocupado "
                        f"por {existing.name}"
                    )

                    self.skipped.append(
                        alias
                    )

                    continue

                # --------------------------------------------
                # CREAR ALIAS
                # --------------------------------------------

                alias_command = self.create_alias_command(
                    command,
                    alias
                )

                try:

                    self.bot.add_command(
                        alias_command
                    )

                    self.registered.append(
                        alias
                    )

                    print(
                        f"[ALIASES] ✅ "
                        f"s{alias} → "
                        f"s{command_name}"
                    )

                except Exception as error:

                    print(
                        f"[ALIASES] ❌ "
                        f"{alias}: "
                        f"{type(error).__name__}: "
                        f"{error}"
                    )

        print("")
        print(
            f"[ALIASES] ✅ "
            f"{len(self.registered)} aliases registrados."
        )

        print(
            f"[ALIASES] ⚠️ "
            f"{len(self.skipped)} aliases omitidos."
        )

        print("=" * 60)

    # ========================================================
    # CREAR COMANDO ALIAS
    # ========================================================

    def create_alias_command(
        self,
        original,
        alias
    ):

        async def alias_callback(ctx, *args, **kwargs):

            await original.callback(
                original.cog,
                ctx,
                *args,
                **kwargs
            )

        # ----------------------------------------------------
        # CREAR COMMAND
        # ----------------------------------------------------

        alias_command = commands.Command(
            alias_callback,
            name=alias,
            help=original.help,
            brief=original.brief,
            description=original.description,
            enabled=original.enabled,
            hidden=original.hidden,
            cooldown_after_parsing=original.cooldown_after_parsing,
            ignore_extra=original.ignore_extra,
            rest_is_raw=original.rest_is_raw,
        )

        # ----------------------------------------------------
        # COPIAR COOLDOWN
        # ----------------------------------------------------

        if original._buckets:

            alias_command._buckets = (
                original._buckets
            )

        # ----------------------------------------------------
        # COPIAR CHECKS
        # ----------------------------------------------------

        alias_command.checks = list(
            original.checks
        )

        # ----------------------------------------------------
        # COPIAR COG
        # ----------------------------------------------------

        alias_command.cog = original.cog

        # ----------------------------------------------------
        # COPIAR PARENT
        # ----------------------------------------------------

        alias_command.parent = original.parent

        return alias_command


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Aliases(bot)
    )