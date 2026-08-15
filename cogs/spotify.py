import discord
from discord.ext import commands
from discord import app_commands
import time
# ============================================================
# CONFIGURACIÓN
# ============================================================
PURPLE = discord.Color.from_rgb(120, 55, 220)
# ============================================================
# COG SPOTIFY
# ============================================================
class Spotify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("[SPOTIFY] Cog cargado.")
    # ========================================================
    # BUSCAR SPOTIFY
    # ========================================================
    def get_spotify(self, member: discord.Member):
        for activity in member.activities:
            if isinstance(activity, discord.Spotify):
                return activity
        return None
    # ========================================================
    # FORMATEAR TIEMPO
    # ========================================================
    def format_time(self, milliseconds):
        seconds = max(
            0,
            int(milliseconds / 1000)
        )
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    # ========================================================
    # BARRA DE PROGRESO
    # ========================================================
    def progress_bar(
        self,
        current,
        total,
        length=18
    ):
        if total <= 0:
            return "━━━━━━━━━━━━━━━━━━"
        percentage = current / total
        percentage = max(
            0,
            min(
                percentage,
                1
            )
        )
        filled = int(
            percentage * length
        )
        empty = length - filled
        if filled >= length:
            return "━" * (length - 1) + "🔘"
        return (
            "━" * filled
            + "🔘"
            + "━" * max(
                0,
                empty - 1
            )
        )
    # ========================================================
    # CREAR EMBED
    # ========================================================
    def create_embed(
        self,
        member,
        spotify
    ):
        # ----------------------------------------------------
        # TIEMPO ACTUAL
        # ----------------------------------------------------
        now = int(
            time.time() * 1000
        )
        start_ms = int(
            spotify.start.timestamp() * 1000
        )
        end_ms = int(
            spotify.end.timestamp() * 1000
        )
        elapsed = now - start_ms
        duration = end_ms - start_ms
        elapsed = max(
            0,
            min(
                elapsed,
                duration
            )
        )
        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------
        embed = discord.Embed(
            title="🎧・NOW PLAYING",
            description=(
                f"**{member.display_name}** está escuchando Spotify.\n\n"
                f"🎵 **{spotify.title}**\n"
                f"👤 **{spotify.artist}**\n"
                f"💿 **{spotify.album}**\n\n"
                f"{self.progress_bar(elapsed, duration)}\n"
                f"`{self.format_time(elapsed)}` "
                f"/ `{self.format_time(duration)}`"
            ),
            color=PURPLE
        )
        # ----------------------------------------------------
        # PORTADA
        # ----------------------------------------------------
        if spotify.album_cover_url:
            embed.set_thumbnail(
                url=spotify.album_cover_url
            )
        # ----------------------------------------------------
        # AUTOR
        # ----------------------------------------------------
        embed.set_author(
            name=member.display_name,
            icon_url=member.display_avatar.url
        )
        # ----------------------------------------------------
        # FOOTER
        # ----------------------------------------------------
        embed.set_footer(
            text="Spotify • Discord Rich Presence"
        )
        return embed
    # ========================================================
    # BOTÓN
    # ========================================================
    class SpotifyView(discord.ui.View):
        def __init__(
            self,
            spotify_url
        ):
            super().__init__(
                timeout=300
            )
            self.add_item(
                discord.ui.Button(
                    label="Abrir en Spotify",
                    emoji="🎧",
                    style=discord.ButtonStyle.link,
                    url=spotify_url
                )
            )
    # ========================================================
    # /FM + s!FM
    # ========================================================
    @commands.hybrid_command(
        name="fm",
        description="Muestra lo que estás escuchando en Spotify."
    )
    async def fm(
        self,
        ctx
    ):
        # ----------------------------------------------------
        # USUARIO
        # ----------------------------------------------------
        member = ctx.author
        # ----------------------------------------------------
        # BUSCAR SPOTIFY
        # ----------------------------------------------------
        spotify = self.get_spotify(
            member
        )
        # ----------------------------------------------------
        # NO ESTÁ ESCUCHANDO
        # ----------------------------------------------------
        if spotify is None:
            embed = discord.Embed(
                title="🎧・NOW PLAYING",
                description=(
                    "❌ No pude detectar Spotify.\n\n"
                    "Asegurate de:\n"
                    "• Tener Spotify conectado a Discord.\n"
                    "• Estar reproduciendo una canción.\n"
                    "• Tener visible tu actividad de Spotify."
                ),
                color=discord.Color.red()
            )
            embed.set_thumbnail(
                url=member.display_avatar.url
            )
            await ctx.send(
                embed=embed
            )
            return
        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------
        embed = self.create_embed(
            member,
            spotify
        )
        # ----------------------------------------------------
        # BOTÓN SPOTIFY
        # ----------------------------------------------------
        view = self.SpotifyView(
            spotify.track_url
        )
        # ----------------------------------------------------
        # ENVIAR
        # ----------------------------------------------------
        await ctx.send(
            embed=embed,
            view=view
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Spotify(bot)
    )