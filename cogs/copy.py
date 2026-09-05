import re
import io
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
EMOJI_REGEX = re.compile(
    r"<(?P<animated>a)?:(?P<name>[A-Za-z0-9_]+):(?P<id>\d+)>"
)
PURPLE = discord.Color.from_rgb(138, 43, 226)
# ============================================================
# COG
# ============================================================
class Copy(commands.Cog):
    """Comando /copy estilo Emoji.gg."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # ========================================================
    # /copy
    # ========================================================
    @app_commands.command(
        name="copy",
        description="Copia un emoji personalizado para poder guardarlo."
    )
    @app_commands.describe(
        emoji="Emoji personalizado que querés copiar."
    )
    async def copy(
        self,
        interaction: discord.Interaction,
        emoji: str
    ):
        await interaction.response.defer(ephemeral=True)
        # ----------------------------------------------------
        # Buscar emoji dentro del texto
        # ----------------------------------------------------
        match = EMOJI_REGEX.search(emoji.strip())
        if not match:
            embed = discord.Embed(
                title="❌ Emoji no válido",
                description=(
                    "Tenés que pasar un **emoji personalizado de Discord**.\n\n"
                    "Ejemplo:\n"
                    "`/copy :nombre_del_emoji:`"
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        emoji_id = match.group("id")
        emoji_name = match.group("name")
        animated = bool(match.group("animated"))
        # ----------------------------------------------------
        # Crear URL
        # ----------------------------------------------------
        extension = "gif" if animated else "png"
        emoji_url = (
            f"https://cdn.discordapp.com/emojis/"
            f"{emoji_id}.{extension}?size=4096&quality=lossless"
        )
        # ----------------------------------------------------
        # Descargar emoji
        # ----------------------------------------------------
        try:
            timeout = aiohttp.ClientTimeout(total=15)
            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:
                async with session.get(emoji_url) as response:
                    if response.status != 200:
                        embed = discord.Embed(
                            title="❌ No pude copiar el emoji",
                            description=(
                                "Discord no permitió descargar este emoji."
                            ),
                            color=discord.Color.red()
                        )
                        await interaction.followup.send(
                            embed=embed,
                            ephemeral=True
                        )
                        return
                    data = await response.read()
        except aiohttp.ClientError:
            embed = discord.Embed(
                title="❌ Error de conexión",
                description=(
                    "No pude conectarme con Discord para descargar "
                    "el emoji."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        except Exception:
            embed = discord.Embed(
                title="❌ Error",
                description=(
                    "Ocurrió un error inesperado al copiar el emoji."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Preparar archivo
        # ----------------------------------------------------
        filename = f"{emoji_name}.{extension}"
        file = discord.File(
            io.BytesIO(data),
            filename=filename
        )
        # ----------------------------------------------------
        # Embed
        # ----------------------------------------------------
        embed = discord.Embed(
            title="✨ Emoji copiado",
            description=(
                f"**{emoji_name}**\n\n"
                "Guardá el archivo para poder usarlo donde quieras."
            ),
            color=PURPLE
        )
        embed.set_thumbnail(url=emoji_url)
        embed.add_field(
            name="Tipo",
            value="Animado 🌀" if animated else "Normal 🖼️",
            inline=True
        )
        embed.add_field(
            name="Formato",
            value=f"`.{extension}`",
            inline=True
        )
        embed.set_footer(
            text="Sistema de emojis • Copy"
        )
        # ----------------------------------------------------
        # Enviar
        # ----------------------------------------------------
        try:
            await interaction.followup.send(
                embed=embed,
                file=file,
                ephemeral=True
            )
        except discord.HTTPException:
            # Si el archivo es demasiado grande, mostramos
            # igualmente el enlace directo.
            embed = discord.Embed(
                title="✨ Emoji listo",
                description=(
                    f"**{emoji_name}**\n\n"
                    f"[Abrir / guardar emoji]({emoji_url})"
                ),
                color=PURPLE
            )
            embed.set_thumbnail(url=emoji_url)
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
# ============================================================
# SETUP
# ============================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Copy(bot))