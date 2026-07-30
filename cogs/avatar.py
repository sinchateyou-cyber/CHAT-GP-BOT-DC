import io
import discord
from discord import app_commands
from discord.ext import commands


class Avatar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="setavatar",
        description="Cambia la foto de perfil del bot."
    )
    @app_commands.describe(
        imagen="Adjunta la nueva foto de perfil del bot."
    )
    import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# OWNER PRINCIPAL
# ============================================================

MAIN_OWNER_ID = 1460867297500594266


class Avatar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # /setavatar
    # ========================================================

    @app_commands.command(
        name="setavatar",
        description="Cambia la foto de perfil del bot."
    )
    @app_commands.describe(
        imagen="Adjunta la nueva foto de perfil del bot."
    )
    async def setavatar(
        self,
        interaction: discord.Interaction,
        imagen: discord.Attachment
    ):

        if interaction.user.id != MAIN_OWNER_ID:
            await interaction.response.send_message(
                "❌ Solo el owner principal del bot puede usar este comando.",
                ephemeral=True
            )
            return

        if not imagen.content_type or not imagen.content_type.startswith("image/"):
            await interaction.response.send_message(
                "❌ El archivo debe ser una imagen.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            image_data = await imagen.read()

            await self.bot.user.edit(
                avatar=image_data
            )

            await interaction.followup.send(
                "✅ Foto de perfil actualizada correctamente.",
                ephemeral=True
            )

        except discord.HTTPException as error:
            await interaction.followup.send(
                f"❌ No se pudo cambiar la foto de perfil.\n"
                f"Error: `{error}`",
                ephemeral=True
            )

    # ========================================================
    # /setname
    # ========================================================

    @app_commands.command(
        name="setname",
        description="Cambia el nombre de usuario del bot."
    )
    @app_commands.describe(
        nombre="Nuevo nombre del bot."
    )
    async def setname(
        self,
        interaction: discord.Interaction,
        nombre: str
    ):

        if interaction.user.id != MAIN_OWNER_ID:
            await interaction.response.send_message(
                "❌ Solo el owner principal del bot puede usar este comando.",
                ephemeral=True
            )
            return

        try:
            await self.bot.user.edit(
                username=nombre
            )

            await interaction.response.send_message(
                f"✅ El nombre del bot cambió a **{nombre}**.",
                ephemeral=True
            )

        except discord.HTTPException as error:
            await interaction.response.send_message(
                f"❌ No se pudo cambiar el nombre.\n"
                f"Error: `{error}`",
                ephemeral=True
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Avatar(bot))
    async def setavatar(
        self,
        interaction: discord.Interaction,
        imagen: discord.Attachment
    ):

        # Verificar que quien ejecuta el comando sea el owner del bot
        if not await self.bot.is_owner(interaction.user):
            await interaction.response.send_message(
                "❌ No tenés permiso para usar este comando.",
                ephemeral=True
            )
            return

        # Verificar el tipo de archivo
        if not imagen.content_type or not imagen.content_type.startswith("image/"):
            await interaction.response.send_message(
                "❌ El archivo debe ser una imagen.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            # Descargar la imagen
            image_data = await imagen.read()

            # Cambiar el avatar del bot
            await self.bot.user.edit(
                avatar=image_data
            )

            await interaction.followup.send(
                "✅ **Foto de perfil actualizada correctamente.**",
                ephemeral=True
            )

        except discord.HTTPException as error:
            await interaction.followup.send(
                f"❌ No se pudo cambiar la foto de perfil.\n"
                f"Error: `{error}`",
                ephemeral=True
            )

        except Exception as error:
            await interaction.followup.send(
                f"❌ Ocurrió un error inesperado.\n"
                f"Error: `{error}`",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Avatar(bot))