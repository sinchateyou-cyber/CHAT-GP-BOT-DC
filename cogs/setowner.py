import discord
from discord import app_commands
from discord.ext import commands


class SetOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="setowner",
        description="Designa al dueño del bot."
    )
    @app_commands.checks.is_owner()
    async def setowner(
        self,
        interaction: discord.Interaction,
        usuario: discord.User
    ):
        self.bot.owner_id = usuario.id

        await interaction.response.send_message(
            f"👑 **{usuario}** ahora es el dueño del bot."
        )


async def setup(bot):
    await bot.add_cog(SetOwner(bot))