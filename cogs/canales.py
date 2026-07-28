import discord
from discord import app_commands
from discord.ext import commands
class Canales(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ============================================================
    # /CREAR-CANAL
    # ============================================================
    @app_commands.command(
        name="crear-canal",
        description="Crea un nuevo canal de texto."
    )
    @app_commands.describe(
        nombre="Nombre del canal que quieres crear."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def crear_canal(
        self,
        interaction: discord.Interaction,
        nombre: str
    ):
        # Crear canal
        canal = await interaction.guild.create_text_channel(
            name=nombre
        )
        await interaction.response.send_message(
            f"✅ Canal creado correctamente: {canal.mention}",
            ephemeral=True
        )
    # ============================================================
    # /ELIMINAR-CANAL
    # ============================================================
    @app_commands.command(
        name="eliminar-canal",
        description="Elimina el canal actual."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def eliminar_canal(
        self,
        interaction: discord.Interaction
    ):
        canal = interaction.channel
        await interaction.response.send_message(
            "🗑️ Eliminando este canal...",
            ephemeral=True
        )
        await canal.delete(
            reason=f"Eliminado por {interaction.user}"
        )
    # ============================================================
    # MANEJO DE ERRORES
    # ============================================================
    @crear_canal.error
    async def crear_canal_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            await interaction.response.send_message(
                "❌ No tenés permiso para gestionar canales.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Ocurrió un error al crear el canal.",
                ephemeral=True
            )
    @eliminar_canal.error
    async def eliminar_canal_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            await interaction.response.send_message(
                "❌ No tenés permiso para gestionar canales.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "❌ Ocurrió un error al eliminar el canal.",
                ephemeral=True
            )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(Canales(bot))