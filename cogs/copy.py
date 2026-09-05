import re
import io
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
PURPLE = discord.Color.from_rgb(138, 43, 226)
EMOJI_REGEX = re.compile(
    r"<(?P<animated>a)?:(?P<name>[A-Za-z0-9_]+):(?P<id>\d+)>"
)
# ============================================================
# COG
# ============================================================
class Copy(commands.Cog):
    """
    Sistema /copy estilo Emoji.gg.
    Permite copiar un emoji personalizado y agregarlo
    directamente al servidor donde se ejecuta el comando.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    # ========================================================
    # /copy
    # ========================================================
    @app_commands.command(
        name="copy",
        description="Copia un emoji y lo agrega a este servidor."
    )
    @app_commands.describe(
        emoji="El emoji personalizado que querés copiar."
    )
    async def copy(
        self,
        interaction: discord.Interaction,
        emoji: str
    ):
        # ----------------------------------------------------
        # Comprobar servidor
        # ----------------------------------------------------
        if interaction.guild is None:
            embed = discord.Embed(
                title="❌ Solo servidores",
                description=(
                    "Este comando solamente puede utilizarse "
                    "dentro de un servidor."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Comprobar permisos del bot
        # ----------------------------------------------------
        bot_member = interaction.guild.me
        if bot_member is None:
            embed = discord.Embed(
                title="❌ No pude comprobar mis permisos",
                description=(
                    "No pude obtener la información de permisos "
                    "del bot en este servidor."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return
        # Manage Expressions
        if not bot_member.guild_permissions.manage_expressions:
            embed = discord.Embed(
                title="❌ Falta un permiso",
                description=(
                    "Necesito el permiso:\n\n"
                    "**Gestionar expresiones**\n\n"
                    "Dame ese permiso y volvé a utilizar `/copy`."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Buscar emoji
        # ----------------------------------------------------
        emoji = emoji.strip()
        match = EMOJI_REGEX.fullmatch(emoji)
        if not match:
            embed = discord.Embed(
                title="❌ Emoji inválido",
                description=(
                    "Tenés que pasar un **emoji personalizado de Discord**.\n\n"
                    "Ejemplo:\n"
                    "`/copy <:emoji:123456789012345678>`\n\n"
                    "También funciona con emojis animados."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return
        emoji_name = match.group("name")
        emoji_id = match.group("id")
        animated = bool(match.group("animated"))
        # ----------------------------------------------------
        # Comprobar nombre
        # ----------------------------------------------------
        # Discord permite nombres de emojis de 2 a 32 caracteres.
        if len(emoji_name) < 2:
            embed = discord.Embed(
                title="❌ Nombre inválido",
                description=(
                    f"El emoji **{emoji_name}** tiene un nombre "
                    "demasiado corto para Discord."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Comprobar si ya existe
        # ----------------------------------------------------
        existing_emoji = discord.utils.get(
            interaction.guild.emojis,
            name=emoji_name
        )
        if existing_emoji is not None:
            embed = discord.Embed(
                title="⚠️ El emoji ya existe",
                description=(
                    f"Ya existe un emoji llamado **{emoji_name}** "
                    "en este servidor.\n\n"
                    f"{existing_emoji}"
                ),
                color=discord.Color.orange()
            )
            embed.set_thumbnail(
                url=str(existing_emoji.url)
            )
            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # URL del emoji
        # ----------------------------------------------------
        extension = "gif" if animated else "png"
        emoji_url = (
            f"https://cdn.discordapp.com/emojis/"
            f"{emoji_id}.{extension}"
            f"?size=4096&quality=lossless"
        )
        # ----------------------------------------------------
        # Descargar emoji
        # ----------------------------------------------------
        await interaction.response.defer(
            ephemeral=True
        )
        try:
            timeout = aiohttp.ClientTimeout(
                total=20
            )
            async with aiohttp.ClientSession(
                timeout=timeout
            ) as session:
                async with session.get(
                    emoji_url
                ) as response:
                    if response.status != 200:
                        embed = discord.Embed(
                            title="❌ No pude descargar el emoji",
                            description=(
                                "Discord no permitió acceder al archivo "
                                "de este emoji.\n\n"
                                f"Código HTTP: `{response.status}`"
                            ),
                            color=discord.Color.red()
                        )
                        await interaction.followup.send(
                            embed=embed,
                            ephemeral=True
                        )
                        return
                    image_data = await response.read()
        except asyncio.TimeoutError:
            embed = discord.Embed(
                title="❌ Tiempo agotado",
                description=(
                    "La descarga del emoji tardó demasiado. "
                    "Probá nuevamente."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        except aiohttp.ClientError:
            embed = discord.Embed(
                title="❌ Error de conexión",
                description=(
                    "No pude conectarme con Discord para "
                    "descargar el emoji."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        except Exception as error:
            print(
                f"[COPY] Error descargando emoji: {error}"
            )
            embed = discord.Embed(
                title="❌ Error",
                description=(
                    "Ocurrió un error al descargar el emoji."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        # ----------------------------------------------------
        # Crear emoji
        # ----------------------------------------------------
        try:
            new_emoji = await interaction.guild.create_custom_emoji(
                name=emoji_name,
                image=image_data,
                reason=(
                    f"Copiado mediante /copy por "
                    f"{interaction.user} ({interaction.user.id})"
                )
            )
        # ----------------------------------------------------
        # Límite de emojis
        # ----------------------------------------------------
        except discord.HTTPException as error:
            print(
                f"[COPY] Error creando emoji: {error}"
            )
            # Límite de emojis
            if error.status == 30008:
                embed = discord.Embed(
                    title="❌ Límite de emojis alcanzado",
                    description=(
                        "Este servidor no tiene espacio para "
                        "más emojis personalizados."
                    ),
                    color=discord.Color.red()
                )
                await interaction.followup.send(
                    embed=embed,
                    ephemeral=True
                )
                return
            # Nombre inválido
            if error.status == 400:
                embed = discord.Embed(
                    title="❌ Discord rechazó el emoji",
                    description=(
                        "Discord rechazó el emoji.\n\n"
                        "Puede que el nombre o el archivo "
                        "no sea válido."
                    ),
                    color=discord.Color.red()
                )
                await interaction.followup.send(
                    embed=embed,
                    ephemeral=True
                )
                return
            embed = discord.Embed(
                title="❌ No pude agregar el emoji",
                description=(
                    "Discord no permitió agregar este emoji "
                    "al servidor."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        except discord.Forbidden:
            embed = discord.Embed(
                title="❌ Sin permisos",
                description=(
                    "No tengo permiso para crear emojis "
                    "en este servidor.\n\n"
                    "Necesito **Gestionar expresiones**."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        except Exception as error:
            print(
                f"[COPY] Error creando emoji: {error}"
            )
            embed = discord.Embed(
                title="❌ Error inesperado",
                description=(
                    "Ocurrió un error al agregar el emoji."
                ),
                color=discord.Color.red()
            )
            await interaction.followup.send(
                embed=embed,
                ephemeral=True
            )
            return
        # ====================================================
        # ÉXITO
        # ====================================================
        embed = discord.Embed(
            title="✨ Emoji copiado correctamente",
            description=(
                f"## {new_emoji}\n\n"
                f"**Nombre:** `{new_emoji.name}`\n"
                f"**ID:** `{new_emoji.id}`\n"
                f"**Tipo:** "
                f"{'Animado 🌀' if animated else 'Normal 🖼️'}\n\n"
                "El emoji ya fue agregado a este servidor."
            ),
            color=PURPLE
        )
        embed.set_thumbnail(
            url=str(new_emoji.url)
        )
        embed.set_footer(
            text=f"Copiado por {interaction.user}"
        )
        await interaction.followup.send(
            embed=embed,
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot: commands.Bot):
    await bot.add_cog(Copy(bot))