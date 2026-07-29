import discord
from discord.ext import commands
from discord import app_commands
import re


class AntiLink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = {}

    @app_commands.command(
        name="antilink",
        description="Activa o desactiva el sistema anti-links."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.choices(estado=[
        app_commands.Choice(name="Activar", value="on"),
        app_commands.Choice(name="Desactivar", value="off")
    ])
    async def antilink(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str]
    ):
        self.config[interaction.guild.id] = estado.value == "on"

        if estado.value == "on":
            await interaction.response.send_message(
                "🛡️ **Anti-Link activado correctamente.**"
            )
        else:
            await interaction.response.send_message(
                "🔴 **Anti-Link desactivado correctamente.**"
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot or not message.guild:
            return

        if not self.config.get(message.guild.id, False):
            return

        # Detectar links
        patron = r"(https?://\S+|www\.\S+|discord\.gg/\S+)"
        
        if re.search(patron, message.content, re.IGNORECASE):

            # Permitir a moderadores enviar links
            if message.author.guild_permissions.manage_messages:
                return

            try:
                await message.delete()

                await message.channel.send(
                    f"🔗 {message.author.mention}, **no se permiten links en este servidor.**",
                    delete_after=5
                )

            except discord.Forbidden:
                pass


async def setup(bot):
    await bot.add_cog(AntiLink(bot))