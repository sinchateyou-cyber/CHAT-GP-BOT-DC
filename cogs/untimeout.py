import discord
from discord import app_commands
from discord.ext import commands


class UnTimeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="untimeout", description="Quita el timeout a un usuario.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def untimeout(self, interaction: discord.Interaction, usuario: discord.Member):
        try:
            await usuario.timeout(None)

            await interaction.response.send_message(
                f"✅ Se quitó el timeout a **{usuario}**."
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para quitar el timeout.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(UnTimeout(bot))