import discord
from discord import app_commands
from discord.ext import commands
class DeleteRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(
        name="deleterole",
        description="Elimina un rol del servidor."
    )
    @app_commands.describe(
        rol="Rol que quieres eliminar"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def deleterole(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):
        if rol >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ No puedo eliminar ese rol porque está por encima de mi rol más alto.",
                ephemeral=True
            )
        if rol.is_default():
            return await interaction.response.send_message(
                "❌ No puedes eliminar el rol @everyone.",
                ephemeral=True
            )
        try:
            nombre = rol.name
            await rol.delete(
                reason=f"Eliminado por {interaction.user}"
            )
            await interaction.response.send_message(
                f"🗑️ El rol **{nombre}** fue eliminado correctamente."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para eliminar ese rol.",
                ephemeral=True
            )
async def setup(bot):
    await bot.add_cog(DeleteRole(bot))