import discord
from discord import app_commands
from discord.ext import commands
class AddRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @app_commands.command(
        name="addrole",
        description="Añade un rol a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que quieres añadir el rol",
        rol="Rol que quieres añadir"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        rol: discord.Role
    ):
        if rol >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ No puedo asignar ese rol porque está por encima de mi rol más alto.",
                ephemeral=True
            )
        if rol in usuario.roles:
            return await interaction.response.send_message(
                f"⚠️ {usuario.mention} ya tiene el rol {rol.mention}.",
                ephemeral=True
            )
        try:
            await usuario.add_roles(rol)
            await interaction.response.send_message(
                f"✅ Se añadió el rol {rol.mention} a {usuario.mention}."
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para asignar ese rol.",
                ephemeral=True
            )
async def setup(bot):
    await bot.add_cog(AddRole(bot))