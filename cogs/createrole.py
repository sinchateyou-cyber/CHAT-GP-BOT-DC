import discord
from discord import app_commands
from discord.ext import commands
class CreateRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(
        name="createrole",
        description="Crea un nuevo rol en el servidor."
    )
    @app_commands.describe(
        nombre="Nombre del nuevo rol"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def createrole(
        self,
        interaction: discord.Interaction,
        nombre: str
    ):
        try:
            rol = await interaction.guild.create_role(
                name=nombre,
                reason=f"Creado por {interaction.user}"
            )
            await interaction.response.send_message(
                f"✅ Rol creado correctamente: {rol.mention}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para crear roles.",
                ephemeral=True
            )
async def setup(bot):
    await bot.add_cog(CreateRole(bot))