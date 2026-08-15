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
    # ROBOS / APUESTAS
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
        "p",
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
        "p",
        "reproducir",
    ],

    "pause": [
        "pa",
    ],

    "resume": [
        "r",
        "continuar",
    ],

    "skip": [
        "s",
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

    def __init__(
        self,
        bot
    ):

        self.bot = bot
        self.registered = []

    # ========================================================
    # REGISTRAR ALIASES
    # ========================================================

    async def cog_load(
        self
    ):

        await self.register_aliases()

    # ========================================================
    # CREAR ALIAS
    # ========================================================

    async def register_aliases(
        self
    ):

        # Esperamos a que estén cargados los demás cogs
        await discord.utils.sleep_until(
            discord.utils.utcnow()
        )

        for command_name, aliases in ALIASES.items():

            command = self.bot.get_command(
                command_name
            )

            if command is None:

                print(
                    f"[ALIASES] ⚠️ "
                    f"No existe: {command_name}"
                )

                continue

            for alias in aliases:

                # Evitar conflictos
                if self.bot.get_command(alias):

                    print(
                        f"[ALIASES] ⚠️ "
                        f"Alias ocupado: {alias}"
                    )

                    continue

                try:

                    command.add_alias(
                        alias
                    )

                    self.registered.append(
                        alias
                    )

                    print(
                        f"[ALIASES] ✅ "
                        f"s!{alias} → "
                        f"s!{command_name}"
                    )

                except Exception as error:

                    print(
                        f"[ALIASES] ❌ "
                        f"{alias}: {error}"
                    )

        print(
            f"[ALIASES] "
            f"{len(self.registered)} aliases registrados."
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    await bot.add_cog(
        Aliases(bot)
    )