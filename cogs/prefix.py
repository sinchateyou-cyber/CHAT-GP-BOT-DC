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
    "prefix.json"
)

DEFAULT_PREFIX = "s!"

PURPLE = discord.Color.from_rgb(
    115,
    55,
    210
)


# ============================================================
# ASEGURAR CARPETA
# ============================================================

os.makedirs(
    DATA_FOLDER,
    exist_ok=True
)


# ============================================================
# CARGAR PREFIJOS
# ============================================================

def load_prefixes():

    if not os.path.exists(DATA_FILE):

        return {}

    try:

        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, dict):

                return data

    except Exception as error:

        print(
            f"❌ Error cargando prefix.json: {error}"
        )

    return {}


# ============================================================
# GUARDAR PREFIJOS
# ============================================================

def save_prefixes(data):

    try:

        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except Exception as error:

        print(
            f"❌ Error guardando prefix.json: {error}"
        )

        return False


# ============================================================
# OBTENER PREFIJO
# ============================================================

def get_prefix(guild):

    if guild is None:

        return DEFAULT_PREFIX

    prefixes = load_prefixes()

    return prefixes.get(
        str(guild.id),
        DEFAULT_PREFIX
    )


# ============================================================
# PREFIX
# ============================================================

class Prefix(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print(
            "✅ Sistema de prefijos cargado."
        )


    # ========================================================
    # CAMBIAR PREFIX
    #
    # SOLAMENTE PREFIX
    #
    # NO ES SLASH COMMAND
    #
    # ========================================================

    @commands.command(
        name="setprefix"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def setprefix(
        self,
        ctx,
        nuevo_prefix: str = None
    ):

        # ----------------------------------------------------
        # SIN PREFIX
        # ----------------------------------------------------

        if not nuevo_prefix:

            actual = get_prefix(
                ctx.guild
            )

            await ctx.send(
                embed=discord.Embed(
                    title="⚙️・PREFIJO",
                    description=(
                        f"El prefijo actual es:\n\n"
                        f"```{actual}```\n\n"
                        f"Para cambiarlo usá:\n"
                        f"```{actual}setprefix nuevo```"
                    ),
                    color=PURPLE
                )
            )

            return


        # ----------------------------------------------------
        # VALIDACIÓN
        # ----------------------------------------------------

        nuevo_prefix = nuevo_prefix.strip()

        if len(nuevo_prefix) > 5:

            await ctx.send(
                "❌ El prefijo no puede tener más de **5 caracteres**.",
                delete_after=8
            )

            return


        if len(nuevo_prefix) == 0:

            await ctx.send(
                "❌ El prefijo no puede estar vacío.",
                delete_after=8
            )

            return


        # ----------------------------------------------------
        # EVITAR ESPACIOS
        # ----------------------------------------------------

        if " " in nuevo_prefix:

            await ctx.send(
                "❌ El prefijo no puede contener espacios.",
                delete_after=8
            )

            return


        # ----------------------------------------------------
        # CARGAR
        # ----------------------------------------------------

        prefixes = load_prefixes()


        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        prefixes[
            str(ctx.guild.id)
        ] = nuevo_prefix


        if not save_prefixes(prefixes):

            await ctx.send(
                "❌ No pude guardar el nuevo prefijo.",
                delete_after=8
            )

            return


        # ----------------------------------------------------
        # CONFIRMACIÓN
        # ----------------------------------------------------

        embed = discord.Embed(
            title="✅・PREFIJO ACTUALIZADO",
            description=(
                f"El nuevo prefijo de este servidor es:\n\n"
                f"## `{nuevo_prefix}`\n\n"
                f"Ejemplo:\n"
                f"`{nuevo_prefix}balance`\n"
                f"`{nuevo_prefix}help`\n"
                f"`{nuevo_prefix}slots`"
            ),
            color=PURPLE
        )

        embed.set_footer(
            text="El prefijo queda guardado incluso después de un deploy."
        )

        await ctx.send(
            embed=embed
        )

        print(
            f"⚙️ Prefijo cambiado en "
            f"{ctx.guild.name}: "
            f"{nuevo_prefix}"
        )


    # ========================================================
    # PREFIJO ACTUAL
    # ========================================================

    @commands.command(
        name="prefix"
    )
    async def prefix(
        self,
        ctx
    ):

        actual = get_prefix(
            ctx.guild
        )

        embed = discord.Embed(
            title="⚙️・PREFIJO ACTUAL",
            description=(
                f"El prefijo de este servidor es:\n\n"
                f"## `{actual}`"
            ),
            color=PURPLE
        )

        await ctx.send(
            embed=embed
        )


    # ========================================================
    # RESET PREFIX
    # ========================================================

    @commands.command(
        name="resetprefix"
    )
    @commands.has_permissions(
        administrator=True
    )
    async def resetprefix(
        self,
        ctx
    ):

        prefixes = load_prefixes()

        guild_id = str(
            ctx.guild.id
        )

        prefixes.pop(
            guild_id,
            None
        )

        save_prefixes(
            prefixes
        )

        embed = discord.Embed(
            title="🔄・PREFIJO RESTABLECIDO",
            description=(
                f"El prefijo volvió a ser:\n\n"
                f"## `{DEFAULT_PREFIX}`"
            ),
            color=PURPLE
        )

        await ctx.send(
            embed=embed
        )

        print(
            f"🔄 Prefijo restablecido en "
            f"{ctx.guild.name}"
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Prefix(bot)
    )

    print(
        "✅ cogs.prefix listo."
    )