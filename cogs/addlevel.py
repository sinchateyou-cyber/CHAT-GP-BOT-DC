import os
import json

import discord
from discord import app_commands
from discord.ext import commands


DATA_FOLDER = "data"
DATA_FILE = "data/xp.json"


def load_data():

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump({}, file, indent=4)

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception:
        return {}


def save_data(data):

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


class AddLevel(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ========================================================
    # /ADDLEVEL
    # ========================================================

    @app_commands.command(
        name="addlevel",
        description="Agrega niveles a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés agregar niveles.",
        niveles="Cantidad de niveles a agregar."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def addlevel(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        niveles: app_commands.Range[int, 1, 100]
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este comando solo funciona en servidores.",
                ephemeral=True
            )

            return


        data = load_data()

        guild_id = str(
            interaction.guild.id
        )

        user_id = str(
            usuario.id
        )


        # ====================================================
        # CREAR SERVIDOR
        # ====================================================

        if guild_id not in data:
            data[guild_id] = {}


        # ====================================================
        # CREAR USUARIO
        # ====================================================

        if user_id not in data[guild_id]:

            data[guild_id][user_id] = {
                "xp": 0,
                "level": 0
            }


        user_data = data[guild_id][user_id]


        old_level = int(
            user_data.get(
                "level",
                0
            )
        )


        # ====================================================
        # AGREGAR NIVELES
        # ====================================================

        new_level = old_level + niveles


        user_data["level"] = new_level


        # ====================================================
        # GUARDAR
        # ====================================================

        save_data(data)


        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(

            title="🏆 Nivel agregado",

            description=(
                f"Se agregaron **{niveles} niveles** "
                f"a {usuario.mention}."
            ),

            colour=discord.Colour.gold()

        )


        embed.add_field(

            name="📈 Nivel anterior",

            value=f"**{old_level}**",

            inline=True

        )


        embed.add_field(

            name="🏆 Nivel actual",

            value=f"**{new_level}**",

            inline=True

        )


        embed.set_thumbnail(

            url=usuario.display_avatar.url

        )


        embed.set_footer(

            text=(
                f"Nivel agregado por "
                f"{interaction.user}"
            )

        )


        await interaction.response.send_message(

            embed=embed

        )


    # ========================================================
    # MANEJO DE ERRORES
    # ========================================================

    @addlevel.error
    async def addlevel_error(

        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError

    ):

        if isinstance(

            error,

            app_commands.errors.MissingPermissions

        ):

            message = (
                "❌ No tenés permisos para usar "
                "este comando.\n"
                "Necesitás ser **Administrador**."
            )

        else:

            print(
                f"❌ Error en /addlevel: "
                f"{type(error).__name__}: {error}"
            )

            message = (
                "❌ Ocurrió un error al "
                "agregar niveles."
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


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        AddLevel(bot)
    )