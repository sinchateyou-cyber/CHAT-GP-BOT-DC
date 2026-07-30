import discord
import wavelink
from discord import app_commands
from discord.ext import commands


class Play(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="play",
        description="Reproduce una canción."
    )
    @app_commands.describe(
        busqueda="Nombre o URL de la canción."
    )
    async def play(
        self,
        interaction: discord.Interaction,
        busqueda: str
    ):

        await interaction.response.defer()

        if interaction.guild is None:
            return await interaction.followup.send(
                "❌ Este comando solo funciona en un servidor.",
                ephemeral=True
            )

        if not interaction.user.voice:
            return await interaction.followup.send(
                "❌ Tenés que estar conectado a un canal de voz.",
                ephemeral=True
            )

        canal = interaction.user.voice.channel
        player = interaction.guild.voice_client

        try:

            # ================================================
            # CONECTAR AL CANAL DE VOZ
            # ================================================

            if player is None:

                player = await canal.connect(
                    cls=wavelink.Player
                )

            elif player.channel != canal:

                await player.move_to(
                    canal
                )

            # ================================================
            # BUSCAR CANCIÓN
            # ================================================

            resultados = await wavelink.Playable.search(
                f"ytsearch:{busqueda}"
            )

            if not resultados:

                return await interaction.followup.send(
                    "❌ No encontré ninguna canción."
                )

            # ================================================
            # OBTENER PRIMER RESULTADO
            # ================================================

            track = resultados[0]

            # ================================================
            # REPRODUCIR
            # ================================================

            await player.play(
                track
            )

            # ================================================
            # EMBED
            # ================================================

            embed = discord.Embed(
                title="🎵 Reproduciendo ahora",
                description=f"**{track.title}**",
                color=discord.Color.blurple()
            )

            if track.author:

                embed.add_field(
                    name="🎤 Artista",
                    value=track.author,
                    inline=True
                )

            if track.length:

                minutos = (
                    track.length // 60000
                )

                segundos = (
                    track.length // 1000
                ) % 60

                embed.add_field(
                    name="⏱️ Duración",
                    value=f"{minutos}:{segundos:02d}",
                    inline=True
                )

            await interaction.followup.send(
                embed=embed
            )

        except Exception as e:

            print(
                "========================================"
            )

            print(
                "❌ ERROR EN /PLAY"
            )

            print(
                f"Tipo: {type(e).__name__}"
            )

            print(
                f"Error: {e}"
            )

            print(
                "========================================"
            )

            await interaction.followup.send(
                f"❌ Error al reproducir:\n"
                f"`{type(e).__name__}: {e}`",
                ephemeral=True
            )


async def setup(bot: commands.Bot):

    await bot.add_cog(
        Play(bot)
    )