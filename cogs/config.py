import discord
from discord import app_commands
from discord.ext import commands

OWNER_ID = 123456789012345678  # Cambialo por tu ID


class Owner(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="owner",
        description="Muestra quién es el dueño del bot."
    )
    async def owner(
        self,
        interaction: discord.Interaction
    ):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                "❌ No tenés permiso para usar este comando.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"👑 El dueño de **{self.bot.user.name}** es "
            f"{interaction.user.mention}.",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Owner(bot))