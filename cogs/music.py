import discord
import wavelink

from discord import app_commands
from discord.ext import commands


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================================================
    # CONECTAR AL CANAL DE VOZ
    # =========================================================

    async def connect_player(self, interaction: discord.Interaction):

        if not interaction.user.voice:
            await interaction.followup.send(
                "❌ Tenés que estar conectado a un canal de voz.",
                ephemeral=True
            )
            return None

        channel = interaction.user.voice.channel
        player = interaction.guild.voice_client

        if player is None:
            player = await channel.connect(cls=wavelink.Player)

        elif player.channel != channel:
            await player.move_to(channel)

        return player

    # =========================================================
    # /PLAY
    # =========================================================

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

        player = await self.connect_player(interaction)

        if player is None:
            return

        try:
            resultados = await wavelink.Playable.search(busqueda)

            if not resultados:
                return await interaction.followup.send(
                    "❌ No encontré ninguna canción."
                )

            track = resultados[0]

            await player.play(track)

            embed = discord.Embed(
                title="🎵 Reproduciendo",
                description=f"**{track.title}**",
                color=discord.Color.blurple()
            )

            if track.author:
                embed.add_field(
                    name="Artista",
                    value=track.author,
                    inline=True
                )

            if track.length:
                minutos = track.length // 60000
                segundos = (track.length // 1000) % 60

                embed.add_field(
                    name="Duración",
                    value=f"{minutos}:{segundos:02d}",
                    inline=True
                )

            await interaction.followup.send(embed=embed)

        except Exception as e:

            print(f"Error en /play: {e}")

            await interaction.followup.send(
                "❌ Ocurrió un error al reproducir la canción."
            )

    # =========================================================
    # /PAUSE
    # =========================================================

    @app_commands.command(
        name="pause",
        description="Pausa la canción actual."
    )
    async def pause(
        self,
        interaction: discord.Interaction
    ):

        player = interaction.guild.voice_client

        if not player:
            return await interaction.response.send_message(
                "❌ El bot no está conectado a un canal de voz.",
                ephemeral=True
            )

        await player.pause(True)

        await interaction.response.send_message(
            "⏸️ Música pausada."
        )

    # =========================================================
    # /RESUME
    # =========================================================

    @app_commands.command(
        name="resume",
        description="Reanuda la canción pausada."
    )
    async def resume(
        self,
        interaction: discord.Interaction
    ):

        player = interaction.guild.voice_client

        if not player:
            return await interaction.response.send_message(
                "❌ El bot no está conectado a un canal de voz.",
                ephemeral=True
            )

        await player.pause(False)

        await interaction.response.send_message(
            "▶️ Música reanudada."
        )

    # =========================================================
    # /SKIP
    # =========================================================

    @app_commands.command(
        name="skip",
        description="Salta la canción actual."
    )
    async def skip(
        self,
        interaction: discord.Interaction
    ):

        player = interaction.guild.voice_client

        if not player:
            return await interaction.response.send_message(
                "❌ El bot no está conectado a un canal de voz.",
                ephemeral=True
            )

        if not player.current:
            return await interaction.response.send_message(
                "❌ No hay ninguna canción reproduciéndose.",
                ephemeral=True
            )

        await player.stop()

        await interaction.response.send_message(
            "⏭️ Canción saltada."
        )

    # =========================================================
    # /STOP
    # =========================================================

    @app_commands.command(
        name="stop",
        description="Detiene la música actual."
    )
    async def stop(
        self,
        interaction: discord.Interaction
    ):

        player = interaction.guild.voice_client

        if not player:
            return await interaction.response.send_message(
                "❌ El bot no está conectado a un canal de voz.",
                ephemeral=True
            )

        await player.stop()

        await interaction.response.send_message(
            "⏹️ Música detenida."
        )

    # =========================================================
    # /QUEUE
    # =========================================================

    @app_commands.command(
        name="queue",
        description="Muestra la cola de canciones."
    )
    async def queue(
        self,
        interaction: discord.Interaction
    ):

        player = interaction.guild.voice_client

        if not player:
            return await interaction.response.send_message(
                "❌ El bot no está conectado a un canal de voz.",
                ephemeral=True
            )

        if not player.current:
            return await interaction.response.send_message(
                "📭 No hay ninguna canción reproduciéndose."
            )

        embed = discord.Embed(
            title="🎵 Música actual",
            description=f"**{player.current.title}**",
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(
            embed=embed
        )

    # =========================================================
    # /LEAVE
    # =========================================================

    @app_commands.command(
        name="leave",
        description="Hace que el bot salga del canal de voz."
    )
    async def leave(
        self,
        interaction: discord.Interaction
    ):

        player = interaction.guild.voice_client

        if not player:
            return await interaction.response.send_message(
                "❌ El bot no está conectado a un canal de voz.",
                ephemeral=True
            )

        await player.disconnect()

        await interaction.response.send_message(
            "👋 Salí del canal de voz."
        )


# =============================================================
# CARGAR COG
# =============================================================

async def setup(bot):
    await bot.add_cog(Music(bot))