import os
import discord
import wavelink
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN DE LAVALINK
# ============================================================
LAVALINK_HOST = os.getenv(
    "LAVALINK_HOST",
    "78.154.103.38"
)
LAVALINK_PORT = int(
    os.getenv(
        "LAVALINK_PORT",
        "14011"
    )
)
LAVALINK_PASSWORD = os.getenv(
    "LAVALINK_PASSWORD",
    "CAMBIAR_CONTRASEÑA"
)
# ============================================================
# COG PRINCIPAL DE MÚSICA
# ============================================================
class Music(commands.Cog):
    def __init__(
        self,
        bot: commands.Bot
    ):
        self.bot = bot
        self.lavalink_connected = False
        # Cola por servidor
        self.queues = {}
    # ========================================================
    # CONECTAR LAVALINK
    # ========================================================
    async def connect_lavalink(self):
        if self.lavalink_connected:
            return
        try:
            node = wavelink.Node(
                identifier="WispByte-Lavalink",
                uri=(
                    f"http://"
                    f"{LAVALINK_HOST}:"
                    f"{LAVALINK_PORT}"
                ),
                password=LAVALINK_PASSWORD
            )
            await wavelink.Pool.connect(
                nodes=[node],
                client=self.bot
            )
            self.lavalink_connected = True
            print(
                "========================================"
            )
            print(
                "✅ Lavalink conectado correctamente."
            )
            print(
                f"🌐 Host: {LAVALINK_HOST}"
            )
            print(
                f"🔌 Puerto: {LAVALINK_PORT}"
            )
            print(
                "========================================"
            )
        except Exception as e:
            print(
                "========================================"
            )
            print(
                "❌ ERROR AL CONECTAR CON LAVALINK"
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
    # ========================================================
    # BOT LISTO
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
                "❌ Este comando solo funciona en un servidor.",
                ephemeral=True
            )
            return None
        if not interaction.user.voice:
            await interaction.followup.send(
                "❌ Tenés que estar conectado a un canal de voz.",
                ephemeral=True
            )
            return None
        voice_channel = (
            interaction.user.voice.channel
        )
        player = (
            interaction.guild.voice_client
        )
        # ----------------------------------------------------
        # CONECTAR BOT
        # ----------------------------------------------------
        if player is None:
            try:
                player = await voice_channel.connect(
                    cls=wavelink.Player
                )
            except Exception as e:
                print(
                    "❌ Error conectando al canal de voz:"
                )
                print(
                    f"{type(e).__name__}: {e}"
                )
                await interaction.followup.send(
                    "❌ No pude conectarme al canal de voz.",
                    ephemeral=True
                )
                return None
        # ----------------------------------------------------
        # MOVER BOT
        # ----------------------------------------------------
        elif player.channel != voice_channel:
            try:
                await player.move_to(
                    voice_channel
                )
            except Exception as e:
                print(
                    "❌ Error moviendo el bot:"
                )
                print(
                    f"{type(e).__name__}: {e}"
                )
                await interaction.followup.send(
                    "❌ No pude moverme a tu canal de voz.",
                    ephemeral=True
                )
                return None
        return player
    # ========================================================
    # OBTENER COLA
    # ========================================================
    def get_queue(
        self,
        guild_id: int
    ):
        if guild_id not in self.queues:
            self.queues[guild_id] = []
        return self.queues[guild_id]
# ============================================================
# CARGAR COG
# ============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        Music(bot)
    )