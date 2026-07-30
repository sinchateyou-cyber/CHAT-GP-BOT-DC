import discord
from discord import app_commands
from discord.ext import commands
class Stop(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot
        self.music = bot.get_cog(
            "Music"
        )
    # ========================================================
    # /STOP
    # ========================================================
    @app_commands.command(
        name="stop",
        description="Detiene la música y limpia la cola."
    )
    async def stop(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(
            ephemeral=True
        )
        # ----------------------------------------------------
        # COMPROBAR MUSIC COG
        # ----------------------------------------------------
        if self.music is None:
            return await interaction.followup.send(
                "❌ El sistema de música no está cargado.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # COMPROBAR SERVIDOR
        # ----------------------------------------------------
        if interaction.guild is None:
            return await interaction.followup.send(
                "❌ Este comando solo funciona en un servidor.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # PLAYER
        # ----------------------------------------------------
        player = (
            interaction.guild.voice_client
        )
        if player is None:
            return await interaction.followup.send(
                "❌ El bot no está conectado a un canal de voz.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # LIMPIAR COLA
        # ----------------------------------------------------
        queue = self.music.get_queue(
            interaction.guild.id
        )
        queue.clear()
        # ----------------------------------------------------
        # DETENER
        # ----------------------------------------------------
        await player.stop()
        await interaction.followup.send(
            "⏹️ Música detenida y cola limpiada.",
            ephemeral=True
        )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        Stop(bot)
    )