import time
import platform
import discord
from discord import app_commands
from discord.ext import commands
class BotInfo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Momento exacto en el que se cargó el Cog
        self.start_time = time.time()
    # =========================================================
    # CALCULAR TIEMPO ACTIVO
    # =========================================================
    def get_uptime(self):
        uptime = int(
            time.time() - self.start_time
        )
        days, remainder = divmod(
            uptime,
            86400
        )
        hours, remainder = divmod(
            remainder,
            3600
        )
        minutes, seconds = divmod(
            remainder,
            60
        )
        partes = []
        if days:
            partes.append(
                f"{days}d"
            )
        if hours:
            partes.append(
                f"{hours}h"
            )
        if minutes:
            partes.append(
                f"{minutes}m"
            )
        if seconds or not partes:
            partes.append(
                f"{seconds}s"
            )
        return " ".join(
            partes
        )
    # =========================================================
    # /BOTINFO
    # =========================================================
    @app_commands.command(
        name="botinfo",
        description="Muestra información completa del bot."
    )
    async def botinfo(
        self,
        interaction: discord.Interaction
    ):
        bot_user = self.bot.user
        if bot_user is None:
            return await interaction.response.send_message(
                "❌ El bot todavía no está completamente iniciado.",
                ephemeral=True
            )
        # =====================================================
        # INFORMACIÓN DEL BOT
        # =====================================================
        avatar_url = (
            bot_user.display_avatar.url
        )
        bot_name = (
            bot_user.name
        )
        bot_id = (
            bot_user.id
        )
        # =====================================================
        # SERVIDORES
        # =====================================================
        servers = len(
            self.bot.guilds
        )
        # =====================================================
        # USUARIOS
        # =====================================================
        users = sum(
            guild.member_count or 0
            for guild in self.bot.guilds
        )
        # =====================================================
        # LAVALINK
        # =====================================================
        lavalink_status = "🔴 Desconectado"
        try:
            if self.bot.voice_clients:
                lavalink_status = "🟢 Conectado"
            else:
                lavalink_status = "🟢 Disponible"
        except Exception:
            lavalink_status = "⚪ Desconocido"
        # =====================================================
        # CREAR EMBED
        # =====================================================
        embed = discord.Embed(
            title=f"🤖 {bot_name}",
            description=(
                "✨ **Información del bot**\n\n"
                "Un bot moderno para administrar, "
                "proteger y mejorar tu servidor."
            ),
            color=discord.Color.blurple(),
            timestamp=discord.utils.utcnow()
        )
        # =====================================================
        # FOTO DEL BOT
        # =====================================================
        embed.set_thumbnail(
            url=avatar_url
        )
        # =====================================================
        # ESTADO
        # =====================================================
        embed.add_field(
            name="🟢 Estado",
            value=(
                "Online"
            ),
            inline=True
        )
        # =====================================================
        # UPTIME
        # =====================================================
        embed.add_field(
            name="⏱️ Tiempo activo",
            value=(
                f"`{self.get_uptime()}`"
            ),
            inline=True
        )
        # =====================================================
        # SERVIDORES
        # =====================================================
        embed.add_field(
            name="🌐 Servidores",
            value=(
                f"`{servers}`"
            ),
            inline=True
        )
        # =====================================================
        # USUARIOS
        # =====================================================
        embed.add_field(
            name="👥 Usuarios",
            value=(
                f"`{users}`"
            ),
            inline=True
        )
        # =====================================================
        # LAVALINK
        # =====================================================
        embed.add_field(
            name="🎵 Lavalink",
            value=(
                lavalink_status
            ),
            inline=True
        )
        # =====================================================
        # ID DEL BOT
        # =====================================================
        embed.add_field(
            name="🆔 ID",
            value=(
                f"`{bot_id}`"
            ),
            inline=True
        )
        # =====================================================
        # INFORMACIÓN TÉCNICA
        # =====================================================
        embed.add_field(
            name="💻 Sistema",
            value=(
                f"Python `{platform.python_version()}`\n"
                f"discord.py `{discord.__version__}`"
            ),
            inline=True
        )
        # =====================================================
        # LATENCIA
        # =====================================================
        ping = round(
            self.bot.latency * 1000
        )
        embed.add_field(
            name="📡 Latencia",
            value=(
                f"`{ping}ms`"
            ),
            inline=True
        )
        # =====================================================
        # USUARIO QUE EJECUTÓ EL COMANDO
        # =====================================================
        embed.set_footer(
            text=(
                f"Solicitado por "
                f"{interaction.user.display_name}"
            ),
            icon_url=(
                interaction.user.display_avatar.url
            )
        )
        # =====================================================
        # ENVIAR EMBED
        # =====================================================
        await interaction.response.send_message(
            embed=embed
        )
# =============================================================
# CARGAR COG
# =============================================================
async def setup(
    bot: commands.Bot
):
    await bot.add_cog(
        BotInfo(bot)
    )