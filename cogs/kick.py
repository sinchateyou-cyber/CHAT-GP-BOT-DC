import discord
from discord import app_commands
from discord.ext import commands


class Kick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Expulsa a un usuario del servidor.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, usuario: discord.Member, razon: str = "Sin razón especificada"):
        if usuario == interaction.user:
            return await interaction.response.send_message(
                "❌ No podés expulsarte a vos mismo.",
                ephemeral=True
            )

        try:
            await usuario.kick(reason=razon)
            await interaction.response.send_message(
                f"👢 **{usuario}** fue expulsado.\n📝 Razón: {razon}"
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para expulsar a este usuario.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Kick(bot))