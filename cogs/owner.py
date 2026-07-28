import discord
from discord import app_commands
from discord.ext import commands
class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # OWNER
    # =========================
    @app_commands.command(
        name="owner",
        description="Muestra información sobre el dueño del bot."
    )
    async def owner(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="👑 Dueño del Bot",
            description=(
                "Este bot fue creado y desarrollado "
                "por su propietario."
            ),
            color=discord.Color.gold()
        )
        embed.add_field(
            name="👤 Owner",
            value="Valentin",
            inline=False
        )
        embed.add_field(
            name="🤖 Bot",
            value=self.bot.user.mention,
            inline=False
        )
        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )
        embed.set_footer(
            text="Gracias por usar el bot."
        )
        await interaction.response.send_message(
            embed=embed
        )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Owner(bot)
    )