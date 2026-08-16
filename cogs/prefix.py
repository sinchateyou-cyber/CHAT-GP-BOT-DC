import discord
from discord.ext import commands
import json
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(
    DATA_FOLDER,
    "prefixes.json"
)

DEFAULT_PREFIX = "s!"


# ============================================================
# CARGAR PREFIJOS
# ============================================================

def cargar_prefijos():

    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )

    if not os.path.exists(DATA_FILE):

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {},
                f,
                indent=4,
                ensure_ascii=False
            )

        return {}

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

            if isinstance(data, dict):
                return data

    except Exception as error:

        print(
            f"[PREFIX] Error cargando: {error}"
        )

    return {}


# ============================================================
# GUARDAR
# ============================================================

def guardar_prefijos(data):

    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )

    with open(
        DATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# COG
# ============================================================

class Prefix(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.prefixes = cargar_prefijos()

        print(
            "[PREFIX] Sistema cargado."
        )


    # ========================================================
    # OBTENER PREFIJO
    # ========================================================

    def get_prefix(
        self,
        guild_id
    ):

        return self.prefixes.get(
            str(guild_id),
            DEFAULT_PREFIX
        )


    # ========================================================
    # SET PREFIX
    # ========================================================

    @commands.hybrid_command(
        name="setprefix",
        description="Cambia el prefijo del bot en este servidor."
    )
    @commands.has_permissions(
        administrator=True
    )
    @discord.app_commands.describe(
        nuevo="Nuevo prefijo del bot."
    )
    async def setprefix(
        self,
        ctx,
        nuevo: str
    ):

        # ----------------------------------------------------
        # VALIDAR
        # ----------------------------------------------------

        if len(nuevo) > 5:

            await ctx.send(
                "❌ El prefijo puede tener "
                "como máximo **5 caracteres**."
            )

            return

        if nuevo.isspace():

            await ctx.send(
                "❌ El prefijo no puede ser solamente espacios."
            )

            return

        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        guild_id = str(
            ctx.guild.id
        )

        self.prefixes[guild_id] = nuevo

        guardar_prefijos(
            self.prefixes
        )

        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------

        embed = discord.Embed(
            title="⚙️・PREFIJO ACTUALIZADO",
            description=(
                f"El nuevo prefijo es:\n\n"
                f"💜 **`{nuevo}`**\n\n"
                f"Ejemplo:\n"
                f"`{nuevo}help`\n"
                f"`{nuevo}slots 500`\n"
                f"`{nuevo}balance`"
            ),
            color=discord.Color.from_rgb(
                115,
                55,
                210
            )
        )

        embed.set_footer(
            text="Configuración del servidor"
        )

        await ctx.send(
            embed=embed
        )


    # ========================================================
    # PREFIX
    # ========================================================

    @commands.hybrid_command(
        name="prefix",
        description="Muestra el prefijo actual."
    )
    async def prefix(
        self,
        ctx
    ):

        prefijo = self.get_prefix(
            ctx.guild.id
        )

        embed = discord.Embed(
            title="💜・PREFIJO",
            description=(
                f"El prefijo de este servidor es:\n\n"
                f"**`{prefijo}`**\n\n"
                f"Ejemplo:\n"
                f"`{prefijo}help`"
            ),
            color=discord.Color.from_rgb(
                115,
                55,
                210
            )
        )

        await ctx.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Prefix(bot)
    )