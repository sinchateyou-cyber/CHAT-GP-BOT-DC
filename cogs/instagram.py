import json
import re
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "instagram.json"


# ============================================================
# DATOS
# ============================================================

def cargar_datos():

    DATA_FOLDER.mkdir(exist_ok=True)

    if not DATA_FILE.exists():

        DATA_FILE.write_text(
            "{}",
            encoding="utf-8"
        )

    try:

        return json.loads(
            DATA_FILE.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return {}


def guardar_datos(data):

    DATA_FOLDER.mkdir(exist_ok=True)

    DATA_FILE.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# COG
# ============================================================

class Instagram(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.data = cargar_datos()

    # ========================================================
    # /instagram
    # ========================================================

    @app_commands.command(
        name="instagram",
        description="Registrá tu Instagram en el servidor."
    )
    @app_commands.describe(
        usuario="Tu usuario de Instagram."
    )
    async def instagram(
        self,
        interaction: discord.Interaction,
        usuario: str
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # LIMPIAR ENTRADA
        # ----------------------------------------------------

        usuario = usuario.strip()

        usuario = usuario.replace(
            "https://instagram.com/",
            ""
        )

        usuario = usuario.replace(
            "https://www.instagram.com/",
            ""
        )

        usuario = usuario.replace(
            "http://instagram.com/",
            ""
        )

        usuario = usuario.replace(
            "@",
            ""
        )

        usuario = usuario.split("?")[0]
        usuario = usuario.split("/")[0]

        # ----------------------------------------------------
        # VALIDAR
        # ----------------------------------------------------

        if not re.fullmatch(
            r"[A-Za-z0-9._]{1,30}",
            usuario
        ):

            return await interaction.response.send_message(
                "❌ Ese usuario de Instagram no parece válido.",
                ephemeral=True
            )

        guild_id = str(
            interaction.guild.id
        )

        user_id = str(
            interaction.user.id
        )

        if guild_id not in self.data:

            self.data[guild_id] = {}

        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        self.data[guild_id][user_id] = {

            "username":
                usuario,

            "display_name":
                interaction.user.display_name
        }

        guardar_datos(
            self.data
        )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="📸 Instagram registrado",
            description=(
                f"**{interaction.user.display_name}** "
                "registró su Instagram.\n\n"
                f"📷 **Instagram:** `@{usuario}`\n"
                f"🔗 https://www.instagram.com/{usuario}/"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_thumbnail(
            url=interaction.user.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ========================================================
    # /verig
    # ========================================================

    @app_commands.command(
        name="verig",
        description="Muestra el Instagram registrado de un usuario."
    )
    @app_commands.describe(
        usuario="Usuario de Discord."
    )
    async def verig(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member = None
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        if usuario is None:

            usuario = interaction.user

        guild_id = str(
            interaction.guild.id
        )

        user_id = str(
            usuario.id
        )

        datos = self.data.get(
            guild_id,
            {}
        ).get(
            user_id
        )

        if not datos:

            return await interaction.response.send_message(
                f"❌ **{usuario.display_name}** "
                "todavía no registró su Instagram.",
                ephemeral=True
            )

        nombre = datos.get(
            "username",
            "desconocido"
        )

        embed = discord.Embed(
            title="📸 Instagram",
            description=(
                f"### {usuario.display_name}\n\n"
                f"📷 **@{nombre}**\n\n"
                f"🔗 https://www.instagram.com/{nombre}/"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ========================================================
    # /quitarig
    # ========================================================

    @app_commands.command(
        name="quitarig",
        description="Elimina tu Instagram registrado."
    )
    async def quitarig(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        guild_id = str(
            interaction.guild.id
        )

        user_id = str(
            interaction.user.id
        )

        if (
            guild_id not in self.data
            or user_id not in self.data[guild_id]
        ):

            return await interaction.response.send_message(
                "❌ No tenés ningún Instagram registrado.",
                ephemeral=True
            )

        del self.data[guild_id][user_id]

        guardar_datos(
            self.data
        )

        await interaction.response.send_message(
            "✅ Eliminé tu Instagram del servidor.",
            ephemeral=True
        )

    # ========================================================
    # /igs
    # ========================================================

    @app_commands.command(
        name="igs",
        description="Muestra los Instagram registrados del servidor."
    )
    async def igs(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        guild_id = str(
            interaction.guild.id
        )

        usuarios = self.data.get(
            guild_id,
            {}
        )

        if not usuarios:

            return await interaction.response.send_message(
                "📸 Todavía nadie registró su Instagram."
            )

        lineas = []

        for user_id, datos in usuarios.items():

            miembro = interaction.guild.get_member(
                int(user_id)
            )

            if miembro is None:
                continue

            nombre = datos.get(
                "username",
                "desconocido"
            )

            lineas.append(
                f"• {miembro.mention} → "
                f"[@{nombre}](https://www.instagram.com/{nombre}/)"
            )

        if not lineas:

            return await interaction.response.send_message(
                "📸 No hay Instagram registrados actualmente."
            )

        # Evitar embeds/mensajes gigantes
        texto = "\n".join(
            lineas[:50]
        )

        embed = discord.Embed(
            title="📸 Instagram del servidor",
            description=texto,
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_footer(
            text=f"{len(lineas)} Instagram registrados"
        )

        await interaction.response.send_message(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Instagram(bot)
    )
