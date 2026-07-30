import discord
from discord import app_commands
from discord.ext import commands
class Leave(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot
        self.music = bot.get_cog(
            "Music"
        )
    # ========================================================
    # /LEAVE
    # ========================================================
    @app_commands.command(
        name="leave",
        description="Hace que el bot salga del canal de voz."
    )
    async def leave(
        self,
        interaction: discord.Interaction
    ):
        await interaction.response.defer(
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
        if self.music:
            queue = self.music.get_queue(
                interaction.guild.id
            )
            queue.clear()
        # ----------------------------------------------------
        # DESCONECTAR
        # ----------------------------------------------------
        await player.disconnect()
        await interaction.followup.send(
            "👋 Salí del canal de voz y limpié la cola.",
            ephemeral=True
        )
# ============================================================
# CARGAR COG
# ============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        Leave(bot)
    )