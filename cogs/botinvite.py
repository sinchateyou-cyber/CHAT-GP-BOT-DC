import discord
from discord.ext import commands
from discord import app_commands
class Invitar(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(
        name="invitar",
        description="Genera el enlace para añadir el bot a un servidor."
    )
    async def invitar(self, interaction: discord.Interaction):
        # Permisos que tendrá el bot al entrar.
        permisos = discord.Permissions(
            administrator=True
        )
        url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=permisos,
            scopes=("bot", "applications.commands")
        )
        embed = discord.Embed(
            title="🤖 Añadir bot",
            description=(
                "Usá el siguiente enlace para añadir el bot a otro servidor.\n\n"
                "⚠️ Necesitás tener permisos para administrar el servidor."
            ),
            color=discord.Color.blurple()
        )
        view = discord.ui.View()
        boton = discord.ui.Button(
            label="Añadir bot",
            emoji="➕",
            style=discord.ButtonStyle.link,
            url=url
        )
        view.add_item(boton)
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )
async def setup(bot: commands.Bot):
    await bot.add_cog(Invitar(bot))