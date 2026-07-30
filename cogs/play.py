import discord
import wavelink
from discord import app_commands
from discord.ext import commands
class Play(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot
        # Buscar el cog Music
        self.music = bot.get_cog(
            "Music"
        )
    # ========================================================
    # /PLAY
    # ========================================================
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
        # ----------------------------------------------------
        # COMPROBAR MUSIC COG
        # ----------------------------------------------------
        if self.music is None:
            return await interaction.followup.send(
                "❌ El sistema de música no está cargado.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # OBTENER PLAYER
        # ----------------------------------------------------
        player = await self.music.get_player(
            interaction
        )
        if player is None:
            return
        guild_id = interaction.guild.id
        # ----------------------------------------------------
        # OBTENER COLA
        # ----------------------------------------------------
        queue = self.music.get_queue(
            guild_id
        )
        try:
            # ------------------------------------------------
            # BUSCAR CANCIÓN
            # ------------------------------------------------
            resultados = await wavelink.Playable.search(
                busqueda
            )
            if not resultados:
                return await interaction.followup.send(
                    "❌ No encontré ninguna canción."
                )
            # ------------------------------------------------
            # PLAYLIST
            # ------------------------------------------------
            if isinstance(
                resultados,
                wavelink.Playlist
            ):
                tracks = resultados.tracks
                if not tracks:
                    return await interaction.followup.send(
                        "❌ La playlist está vacía."
                    )
                queue.extend(
                    tracks
                )
                if not player.playing:
                    track = queue.pop(
                        0
                    )
                    await player.play(
                        track
                    )
                    return await interaction.followup.send(
                        f"🎵 Reproduciendo playlist "
                        f"**{resultados.name}**.\n"
                        f"📀 Se agregaron "
                        f"**{len(tracks)}** canciones."
                    )
                return await interaction.followup.send(
                    f"📀 Playlist agregada a la cola.\n"
                    f"🎵 Canciones agregadas: "
                    f"**{len(tracks)}**"
                )
            # ------------------------------------------------
            # PRIMER RESULTADO
            # ------------------------------------------------
            track = resultados[0]
            # ------------------------------------------------
            # SI ESTÁ REPRODUCIENDO
            # ------------------------------------------------
            if player.playing:
                queue.append(
                    track
                )
                return await interaction.followup.send(
                    f"📥 Agregado a la cola:\n"
                    f"**{track.title}**\n"
                    f"📌 Posición: "
                    f"**{len(queue)}**"
                )
            # ------------------------------------------------
            # REPRODUCIR
            # ------------------------------------------------
            await player.play(
                track
            )
            # ------------------------------------------------
            # EMBED
            # ------------------------------------------------
            embed = discord.Embed(
                title="🎵 Reproduciendo ahora",
                description=(
                    f"**{track.title}**"
                ),
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
                    value=(
                        f"{minutos}:"
                        f"{segundos:02d}"
                    ),
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
# ============================================================
# CARGAR COG
# ============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        Play(bot)
    )