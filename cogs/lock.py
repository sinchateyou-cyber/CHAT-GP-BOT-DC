import discord
from discord import app_commands
from discord.ext import commands


class Lock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lock", description="Bloquea el canal actual.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        canal = interaction.channel
        permisos = canal.overwrites_for(interaction.guild.default_role)
        permisos.send_messages = False

        await canal.set_permissions(
            interaction.guild.default_role,
            overwrite=permisos
        )

        await interaction.response.send_message(
            "🔒 **Canal bloqueado.** Solo los usuarios con permisos podrán escribir."
        )


async def setup(bot):
    await bot.add_cog(Lock(bot))