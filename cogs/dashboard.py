import os
import discord
from discord.ext import commands
from discord import app_commands
class Dashboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # URL de tu Dashboard en Render
        self.dashboard_url = os.getenv(
            "DASHBOARD_URL",
            "https://TU-DASHBOARD.onrender.com"
        )
    @app_commands.command(
        name="dashboard",
        description="Abre el Dashboard de administración del bot."
    )
    async def dashboard(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="⚙️ Dashboard",
            description=(
                "Administrá tu servidor desde el Dashboard web.\n\n"
                "Podés configurar sistemas de seguridad, "
                "ver información del servidor y administrar "
                "las funciones disponibles."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Dashboard • Tu Bot"
        )
        view = discord.ui.View()
        button = discord.ui.Button(
            label="Abrir Dashboard",
            style=discord.ButtonStyle.link,
            url=self.dashboard_url,
            emoji="🌐"
        )
        view.add_item(button)
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )
async def setup(bot):
    await bot.add_cog(Dashboard(bot))