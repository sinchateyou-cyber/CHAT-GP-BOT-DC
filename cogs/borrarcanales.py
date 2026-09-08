import discord
from discord.ext import commands
from discord import app_commands
class ConfirmarBorrado(discord.ui.View):
    def __init__(self, autor_id: int):
        super().__init__(timeout=30)
        self.autor_id = autor_id
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.autor_id:
            await interaction.response.send_message(
                "❌ Solo la persona que ejecutó el comando puede confirmar.",
                ephemeral=True
            )
            return False
        return True
    @discord.ui.button(
        label="Confirmar borrado",
        style=discord.ButtonStyle.danger,
        emoji="🗑️"
    )
    async def confirmar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de Administrador.",
                ephemeral=True
            )
            return
        await interaction.response.edit_message(
            content="🗑️ **Borrando todos los canales...**",
            view=None
        )
        canales = list(guild.channels)
        eliminados = 0
        errores = 0
        # Ordenamos para intentar eliminar categorías primero.
        canales.sort(
            key=lambda canal: 0 if isinstance(canal, discord.CategoryChannel) else 1
        )
        for canal in canales:
            try:
                await canal.delete(
                    reason=f"Borrado masivo solicitado por {interaction.user}"
                )
                eliminados += 1
            except (discord.Forbidden, discord.HTTPException):
                errores += 1
        try:
            await interaction.followup.send(
                f"🗑️ **Proceso terminado.**\n\n"
                f"• Canales eliminados: **{eliminados}**\n"
                f"• Errores: **{errores}**"
            )
        except discord.HTTPException:
            pass
        self.stop()
    @discord.ui.button(
        label="Cancelar",
        style=discord.ButtonStyle.secondary,
        emoji="❌"
    )
    async def cancelar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.edit_message(
            content="❌ **Borrado cancelado.**",
            view=None
        )
        self.stop()
class BorrarCanales(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(
        name="borrarcanales",
        description="Elimina todos los canales del servidor."
    )
    @app_commands.default_permissions(administrator=True)
    async def borrarcanales(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Necesitás permisos de **Administrador**.",
                ephemeral=True
            )
            return
        canales = interaction.guild.channels
        if not canales:
            await interaction.response.send_message(
                "ℹ️ Este servidor no tiene canales para borrar.",
                ephemeral=True
            )
            return
        await interaction.response.send_message(
            "⚠️ **¿Estás seguro?**\n\n"
            f"Esto va a eliminar **{len(canales)} canales** del servidor.\n"
            "Esta acción **no se puede deshacer**.\n\n"
            "Presioná **Confirmar borrado** para continuar.",
            view=ConfirmarBorrado(interaction.user.id),
            ephemeral=True
        )
async def setup(bot: commands.Bot):
    await bot.add_cog(BorrarCanales(bot))