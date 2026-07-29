import discord
from discord import app_commands
from discord.ext import commands
class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(
        name="clear",
        description="Elimina mensajes del canal."
    )
    @app_commands.describe(
        cantidad="Cantidad de mensajes a eliminar (1-100)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        cantidad: app_commands.Range[int, 1, 100]
    ):
        await interaction.response.defer(ephemeral=True)
        try:
            eliminados = await interaction.channel.purge(
                limit=cantidad
            )
            await interaction.followup.send(
                f"🧹 Se eliminaron **{len(eliminados)} mensajes** correctamente.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "❌ No tengo permisos para eliminar mensajes.",
                ephemeral=True
            )
        except discord.HTTPException:
            await interaction.followup.send(
                "❌ Ocurrió un error al intentar eliminar los mensajes.",
                ephemeral=True
            )
async def setup(bot):
    await bot.add_cog(Clear(bot))