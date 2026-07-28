import discord
from discord import app_commands
from discord.ext import commands
class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # SAY
    # =========================
    @app_commands.command(
        name="say",
        description="Hace que el bot envíe un mensaje."
    )
    @app_commands.describe(
        mensaje="Mensaje que querés que envíe el bot."
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def say(
        self,
        interaction: discord.Interaction,
        mensaje: str
    ):
        await interaction.response.send_message(
            mensaje
        )
    # =========================
    # ERROR SAY
    # =========================
    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            await interaction.response.send_message(
                f"❌ {interaction.user.mention}, "
                "no tenés permisos para usar este comando.",
                ephemeral=True
            )
        else:
            print(
                f"❌ Error en /say: {error}"
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al ejecutar el comando.",
                    ephemeral=True
                )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Say(bot)
    )