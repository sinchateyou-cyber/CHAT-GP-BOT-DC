import discord
from discord import app_commands
from discord.ext import commands


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Banea a un usuario del servidor.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón especificada"):
        if usuario == interaction.user:
            return await interaction.response.send_message(
                "❌ No podés banearte a vos mismo.",
                ephemeral=True
            )

        try:
            await usuario.ban(reason=razon)
            await interaction.response.send_message(
                f"🔨 **{usuario}** fue baneado.\n📝 Razón: {razon}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para banear a este usuario.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Ban(bot))