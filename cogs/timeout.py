import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta


class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="Pone a un usuario en timeout.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        minutos: int,
        razon: str = "Sin razón especificada"
    ):
        if minutos <= 0:
            return await interaction.response.send_message(
                "❌ Los minutos deben ser mayores a 0.",
                ephemeral=True
            )

        try:
            await usuario.timeout(
                timedelta(minutes=minutos),
                reason=razon
            )

            await interaction.response.send_message(
                f"⏱️ **{usuario}** recibió timeout por **{minutos} minutos**.\n📝 Razón: {razon}"
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para aplicar timeout.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Timeout(bot))