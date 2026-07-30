import discord
import wavelink
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN DE LAVALINK
# ============================================================
LAVALINK_HOST = "78.154.103.38"
LAVALINK_PORT = 14011
LAVALINK_PASSWORD = "valentincdz"
class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.lavalink_connected = False
    # ========================================================
    # CONECTAR WAVELINK CON LAVALINK
    # ========================================================
    async def connect_lavalink(self):
        if self.lavalink_connected:
            return
        try:
            node = wavelink.Node(
                identifier="WispByte-Lavalink",
                uri=f"http://{LAVALINK_HOST}:{LAVALINK_PORT}",
                password=LAVALINK_PASSWORD
            )
            await wavelink.Pool.connect(
                nodes=[node],
                client=self.bot
            )
            self.lavalink_connected = True
            print("========================================")
            print("✅ Lavalink conectado correctamente.")
            print(f"🌐 Host: {LAVALINK_HOST}")
            print(f"🔌 Puerto: {LAVALINK_PORT}")
            print("========================================")
        except Exception as e:
            print("========================================")
            print("❌ ERROR AL CONECTAR CON LAVALINK")
            print(f"Tipo: {type(e).__name__}")
            print(f"Error: {e}")
            print("========================================")
    # ========================================================
    # EVENTO CUANDO EL BOT ESTÁ LISTO
    # ========================================================
    @commands.Cog.listener()
    async def on_ready(self):
        if not self.lavalink_connected:
            await self.connect_lavalink()
    # ========================================================
    # OBTENER PLAYER
    # ========================================================
    async def get_player(
        self,
        interaction: discord.Interaction
    ):
        if interaction.guild is None:
            await interaction.followup.send(
                "❌ Este comando solo puede utilizarse en un servidor.",
                ephemeral=True
            )
            return None
        if not interaction.user.voice:
            await interaction.followup.send(
                "❌ Tenés que estar conectado a un canal de voz.",
                ephemeral=True
            )
            return None
        voice_channel = interaction.user.voice.channel
        player = interaction.guild.voice_client
        # ----------------------------------------------------
        # SI EL BOT NO ESTÁ CONECTADO
        # ----------------------------------------------------
        if player is None:
            try:
                player = await voice_channel.connect(
                    cls=wavelink.Player
                )
            except Exception as e:
                print(
                    f"❌ Error conectando al canal de voz: "
                    f"{type(e).__name__}: {e}"
                )
                await interaction.followup.send(
                    "❌ No pude conectarme al canal de voz.",
                    ephemeral=True
                )
                return None
        # ----------------------------------------------------
        # SI EL BOT ESTÁ EN OTRO CANAL
        # ----------------------------------------------------
        elif player.channel != voice_channel:
            try:
                await player.move_to(
                    voice_channel
                )
            except Exception as e:
                print(
                    f"❌ Error moviendo el bot: "
                    f"{type(e).__name__}: {e}"
                )
                await interaction.followup.send(
                    "❌ No pude moverme a tu canal de voz.",
                    ephemeral=True
                )
                return None
        return player
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
        player = await self.get_player(
            interaction
        )
        if player is None:
            return
        try:
            # ------------------------------------------------
            # BUSCAR CANCIÓN
            # ------------------------------------------------
            resultados = await wavelink.Playable.search(busqueda)
            # ------------------------------------------------
            # COMPROBAR RESULTADOS
            # ------------------------------------------------
            if not resultados:
                return await interaction.followup.send(
                    "❌ No encontré ninguna canción."
                )
            # ------------------------------------------------
            # OBTENER PRIMER RESULTADO
            # ------------------------------------------------
            track = resultados[0]
            # ------------------------------------------------
            # REPRODUCIR
            # ------------------------------------------------
            await player.play(
                track
            )
            # ------------------------------------------------
            # CREAR EMBED
            # ------------------------------------------------
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
                minutos = track.length // 60000
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
        # ====================================================
        # MOSTRAR ERROR REAL
        # ====================================================
        except Exception as e:
            import traceback
            print(
                "========================================"
            )
            print(
                "❌ ERROR COMPLETO EN /PLAY"
            )
            print(
                f"Tipo: {type(e).__name__}"
            )
            print(
                f"Error: {e}"
            )
            print(
                "Traceback completo:"
            )
            traceback.print_exc()
            print(
                "========================================"
            )
            await interaction.followup.send(
                f"❌ Error al reproducir:\n"
                f"`{type(e).__name__}: {e}`",
                ephemeral=True
            )
    # ========================================================
    # /PAUSE
    # ========================================================
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
        await player.pause(
            True
        )
        await interaction.response.send_message(
            "⏸️ Música pausada."
        )
    # ========================================================
    # /RESUME
    # ========================================================
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
        await player.pause(
            False
        )
        await interaction.response.send_message(
            "▶️ Música reanudada."
        )
    # ========================================================
    # /SKIP
    # ========================================================
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
        await player.skip()
        await interaction.response.send_message(
            "⏭️ Canción saltada."
        )
    # ========================================================
    # /STOP
    # ========================================================
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
    # ========================================================
    # /QUEUE
    # ========================================================
    @app_commands.command(
        name="queue",
        description="Muestra la canción actual."
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
        track = player.current
        embed = discord.Embed(
            title="🎵 Música actual",
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
            minutos = track.length // 60000
            segundos = (
                track.length // 1000
            ) % 60
            embed.add_field(
                name="⏱️ Duración",
                value=f"{minutos}:{segundos:02d}",
                inline=True
            )
        await interaction.response.send_message(
            embed=embed
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
# ============================================================
# CARGAR COG
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Music(bot)
    )