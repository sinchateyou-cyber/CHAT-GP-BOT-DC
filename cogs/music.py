import discord
from discord.ext import commands
import wavelink


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PLAY
    # =========================

    @commands.command(name="play")
    async def play(self, ctx, *, search: str):

        if not ctx.author.voice:
            return await ctx.send(
                "❌ Tenés que estar conectado a un canal de voz."
            )

        voice_channel = ctx.author.voice.channel
        player = ctx.voice_client

        # Conectar al canal
        if not player:
            try:
                player = await voice_channel.connect(
                    cls=wavelink.Player
                )
            except Exception as e:
                return await ctx.send(
                    f"❌ No pude conectarme al canal de voz.\n`{e}`"
                )

        # Comprobar que estén en el mismo canal
        elif player.channel != voice_channel:
            return await ctx.send(
                "❌ Tenés que estar en el mismo canal de voz que el bot."
            )

        # Buscar canción
        try:
            tracks = await wavelink.Playable.search(search)
        except Exception as e:
            return await ctx.send(
                f"❌ Ocurrió un error al buscar la canción.\n`{e}`"
            )

        if not tracks:
            return await ctx.send(
                "❌ No encontré ninguna canción."
            )

        track = tracks[0]

        # Si ya está reproduciendo, agregar a la cola
        if player.playing:
            await player.queue.put_wait(track)

            return await ctx.send(
                f"🎵 Agregada a la cola: **{track.title}**"
            )

        # Reproducir
        await player.play(track)

        await ctx.send(
            f"▶️ Reproduciendo: **{track.title}**"
        )

    # =========================
    # SKIP
    # =========================

    @commands.command(name="skip")
    async def skip(self, ctx):

        player = ctx.voice_client

        if not player:
            return await ctx.send(
                "❌ El bot no está conectado a un canal de voz."
            )

        if not player.playing:
            return await ctx.send(
                "❌ No hay ninguna canción reproduciéndose."
            )

        await player.skip()

        await ctx.send(
            "⏭️ Canción saltada."
        )

    # =========================
    # STOP
    # =========================

    @commands.command(name="stop")
    async def stop(self, ctx):

        player = ctx.voice_client

        if not player:
            return await ctx.send(
                "❌ El bot no está conectado a un canal de voz."
            )

        await player.stop()
        player.queue.clear()

        await ctx.send(
            "⏹️ Música detenida y cola eliminada."
        )

    # =========================
    # LEAVE
    # =========================

    @commands.command(name="leave")
    async def leave(self, ctx):

        player = ctx.voice_client

        if not player:
            return await ctx.send(
                "❌ No estoy conectado a ningún canal de voz."
            )

        await player.disconnect()

        await ctx.send(
            "👋 Salí del canal de voz."
        )

    # =========================
    # SIGUIENTE CANCIÓN
    # =========================

    @commands.Cog.listener()
    async def on_wavelink_track_end(
        self,
        payload: wavelink.TrackEndEventPayload
    ):

        player = payload.player

        if not player:
            return

        if player.queue:
            next_track = await player.queue.get()
            await player.play(next_track)


async def setup(bot):
    await bot.add_cog(Music(bot))