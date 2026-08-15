# ============================================================
# COGS/STEAM.PY
# Steam Stats SIN Steam Web API Key
# ============================================================

import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
import asyncio
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse


# ============================================================
# CONFIGURACIÓN
# ============================================================

STEAM_TIMEOUT = 12

STEAM_COMMUNITY = "https://steamcommunity.com"

PURPLE = discord.Color.from_rgb(
    145,
    70,
    255
)


# ============================================================
# UTILIDADES
# ============================================================

def limpiar_input(valor: str) -> str:
    """
    Limpia espacios y caracteres innecesarios.
    """

    return valor.strip()


def es_steamid64(valor: str) -> bool:
    """
    Comprueba si el valor parece un SteamID64.
    """

    return (
        valor.isdigit()
        and len(valor) >= 15
    )


def construir_url_perfil(identificador: str) -> str:
    """
    Convierte diferentes formatos a una URL de Steam.
    """

    identificador = limpiar_input(
        identificador
    )

    # --------------------------------------------------------
    # URL completa
    # --------------------------------------------------------

    if identificador.startswith(
        "https://steamcommunity.com/"
    ):

        return identificador.rstrip("/")

    if identificador.startswith(
        "http://steamcommunity.com/"
    ):

        return identificador.rstrip("/")

    # --------------------------------------------------------
    # SteamID64
    # --------------------------------------------------------

    if es_steamid64(identificador):

        return (
            f"{STEAM_COMMUNITY}/profiles/"
            f"{identificador}"
        )

    # --------------------------------------------------------
    # Si pasan solamente un nombre
    # --------------------------------------------------------

    return (
        f"{STEAM_COMMUNITY}/id/"
        f"{identificador}"
    )


def obtener_xml_url(
    perfil_url: str
) -> str:

    return (
        perfil_url.rstrip("/")
        + "/?xml=1"
    )


# ============================================================
# PARSER XML
# ============================================================

def xml_text(
    root,
    tag,
    default=""
):

    elemento = root.find(
        f".//{tag}"
    )

    if elemento is None:
        return default

    if elemento.text is None:
        return default

    return elemento.text.strip()


def xml_int(
    root,
    tag,
    default=0
):

    valor = xml_text(
        root,
        tag,
        ""
    )

    try:
        return int(valor)

    except (
        ValueError,
        TypeError
    ):
        return default


# ============================================================
# DATOS STEAM
# ============================================================

class SteamProfile:

    def __init__(self):

        self.steamid = ""
        self.nickname = ""
        self.realname = ""

        self.avatar = ""

        self.profile_url = ""

        self.online_state = ""
        self.state_message = ""

        self.location = ""

        self.member_since = ""

        self.games_count = 0
        self.groups_count = 0

        self.hours_total = 0.0

        self.raw_xml = None


# ============================================================
# COG
# ============================================================

class Steam(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        print(
            "[STEAM] Cog cargado."
        )


    # ========================================================
    # HTTP
    # ========================================================

    async def fetch_xml(
        self,
        url: str
    ):

        timeout = aiohttp.ClientTimeout(
            total=STEAM_TIMEOUT
        )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Discord Steam Stats Bot)"
            )
        }

        try:

            async with aiohttp.ClientSession(
                timeout=timeout,
                headers=headers
            ) as session:

                async with session.get(
                    url,
                    allow_redirects=True
                ) as response:

                    if response.status != 200:

                        print(
                            "[STEAM] HTTP:",
                            response.status
                        )

                        return None

                    return await response.text(
                        encoding="utf-8",
                        errors="ignore"
                    )

        except asyncio.TimeoutError:

            print(
                "[STEAM] Timeout."
            )

            return None

        except aiohttp.ClientError as error:

            print(
                "[STEAM] HTTP error:",
                error
            )

            return None

        except Exception as error:

            print(
                "[STEAM] Error:",
                error
            )

            return None


    # ========================================================
    # OBTENER PERFIL
    # ========================================================

    async def get_profile(
        self,
        identificador: str
    ):

        perfil_url = construir_url_perfil(
            identificador
        )

        xml_url = obtener_xml_url(
            perfil_url
        )

        contenido = await self.fetch_xml(
            xml_url
        )

        if not contenido:

            return None, "No se pudo acceder al perfil."


        # ----------------------------------------------------
        # Parsear XML
        # ----------------------------------------------------

        try:

            root = ET.fromstring(
                contenido
            )

        except ET.ParseError:

            return None, (
                "Steam no devolvió información "
                "pública del perfil."
            )

        profile = SteamProfile()

        profile.raw_xml = root

        profile.profile_url = (
            xml_text(
                root,
                "profileurl",
                perfil_url
            )
        )

        profile.steamid = (
            xml_text(
                root,
                "steamID64",
                ""
            )
        )

        if not profile.steamid:

            profile.steamid = (
                xml_text(
                    root,
                    "steamID",
                    ""
                )
            )

        profile.nickname = (
            xml_text(
                root,
                "steamID",
                "Usuario de Steam"
            )
        )

        profile.realname = (
            xml_text(
                root,
                "realname",
                ""
            )
        )

        profile.avatar = (
            xml_text(
                root,
                "avatarFull",
                ""
            )
        )

        profile.online_state = (
            xml_text(
                root,
                "onlineState",
                "offline"
            )
        )

        profile.state_message = (
            xml_text(
                root,
                "stateMessage",
                ""
            )
        )

        profile.location = (
            xml_text(
                root,
                "location",
                ""
            )
        )

        profile.member_since = (
            xml_text(
                root,
                "memberSince",
                ""
            )
        )

        profile.games_count = (
            xml_int(
                root,
                "gameCount",
                0
            )
        )

        profile.groups_count = (
            xml_int(
                root,
                "groupCount",
                0
            )
        )

        # ----------------------------------------------------
        # Horas
        # ----------------------------------------------------

        total_minutes = 0

        for game in root.findall(
            ".//game"
        ):

            hours = game.find(
                "hoursPlayed"
            )

            if hours is not None:

                try:

                    total_minutes += (
                        float(
                            hours.text or 0
                        )
                        * 60
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    pass

        profile.hours_total = (
            total_minutes / 60
        )

        return profile, None


    # ========================================================
    # ESTADO
    # ========================================================

    def estado_steam(
        self,
        estado
    ):

        estado = (
            estado or ""
        ).lower()

        estados = {

            "online": (
                "🟢",
                "En línea"
            ),

            "offline": (
                "⚫",
                "Desconectado"
            ),

            "busy": (
                "🔴",
                "Ocupado"
            ),

            "away": (
                "🟡",
                "Ausente"
            ),

            "snooze": (
                "🌙",
                "Ausente"
            ),

            "lookingtotrade": (
                "🔄",
                "Buscando intercambio"
            ),

            "lookingtoplay": (
                "🎮",
                "Buscando jugar"
            )
        }

        return estados.get(
            estado,
            (
                "⚪",
                estado.capitalize()
                if estado
                else "Desconocido"
            )
        )


    # ========================================================
    # EMBED PERFIL
    # ========================================================

    def crear_embed(
        self,
        profile: SteamProfile,
        autor: discord.Member
    ):

        emoji_estado, estado = (
            self.estado_steam(
                profile.online_state
            )
        )

        embed = discord.Embed(
            title=(
                f"🎮・Steam de "
                f"{profile.nickname}"
            ),
            color=PURPLE,
            url=profile.profile_url
        )

        # ----------------------------------------------------
        # Descripción
        # ----------------------------------------------------

        descripcion = (
            f"{emoji_estado} **Estado:** "
            f"{estado}"
        )

        if profile.state_message:

            descripcion += (
                f"\n💬 **Actividad:** "
                f"{profile.state_message}"
            )

        embed.description = (
            descripcion
        )

        # ----------------------------------------------------
        # Avatar
        # ----------------------------------------------------

        if profile.avatar:

            embed.set_thumbnail(
                url=profile.avatar
            )

        # ----------------------------------------------------
        # Información
        # ----------------------------------------------------

        embed.add_field(
            name="🆔 SteamID64",
            value=(
                f"`{profile.steamid or 'No disponible'}`"
            ),
            inline=False
        )

        embed.add_field(
            name="👤 Nombre",
            value=(
                profile.realname
                or "No especificado"
            ),
            inline=True
        )

        embed.add_field(
            name="🎮 Juegos",
            value=(
                str(profile.games_count)
                if profile.games_count
                else "Privado / no disponible"
            ),
            inline=True
        )

        embed.add_field(
            name="⏱️ Horas",
            value=(
                f"{profile.hours_total:,.1f} h"
                if profile.hours_total > 0
                else "No disponible"
            ),
            inline=True
        )

        if profile.location:

            embed.add_field(
                name="🌎 Ubicación",
                value=(
                    profile.location
                ),
                inline=True
            )

        if profile.member_since:

            embed.add_field(
                name="📅 Cuenta",
                value=(
                    profile.member_since
                ),
                inline=True
            )

        if profile.groups_count:

            embed.add_field(
                name="👥 Grupos",
                value=(
                    str(
                        profile.groups_count
                    )
                ),
                inline=True
            )

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        embed.set_footer(
            text=(
                f"Solicitado por "
                f"{autor.display_name}"
            )
        )

        return embed


    # ========================================================
    # /STEAM PERFIL
    # ========================================================

    steam_group = app_commands.Group(
        name="steam",
        description=(
            "Consulta información pública de Steam."
        )
    )


    @steam_group.command(
        name="perfil",
        description=(
            "Muestra las estadísticas públicas "
            "de un perfil de Steam."
        )
    )
    @app_commands.describe(
        usuario=(
            "SteamID64, URL del perfil "
            "o nombre personalizado."
        )
    )
    async def steam_perfil(
        self,
        interaction: discord.Interaction,
        usuario: str
    ):

        await interaction.response.defer()

        profile, error = (
            await self.get_profile(
                usuario
            )
        )

        if error:

            await interaction.followup.send(
                f"❌ {error}"
            )

            return

        embed = self.crear_embed(
            profile,
            interaction.user
        )

        await interaction.followup.send(
            embed=embed
        )


    # ========================================================
    # /STEAM STATS
    # ========================================================

    @steam_group.command(
        name="stats",
        description=(
            "Muestra un resumen de las "
            "estadísticas públicas de Steam."
        )
    )
    @app_commands.describe(
        usuario=(
            "SteamID64 o URL del perfil."
        )
    )
    async def steam_stats(
        self,
        interaction: discord.Interaction,
        usuario: str
    ):

        await interaction.response.defer()

        profile, error = (
            await self.get_profile(
                usuario
            )
        )

        if error:

            await interaction.followup.send(
                f"❌ {error}"
            )

            return

        embed = discord.Embed(
            title=(
                f"📊・Estadísticas de "
                f"{profile.nickname}"
            ),
            color=PURPLE,
            url=profile.profile_url
        )

        if profile.avatar:

            embed.set_thumbnail(
                url=profile.avatar
            )

        embed.add_field(
            name="🆔 SteamID64",
            value=(
                f"`{profile.steamid or 'N/A'}`"
            ),
            inline=False
        )

        embed.add_field(
            name="🎮 Juegos",
            value=(
                str(profile.games_count)
                if profile.games_count
                else "Privado"
            ),
            inline=True
        )

        embed.add_field(
            name="⏱️ Horas totales",
            value=(
                f"{profile.hours_total:,.1f}"
                if profile.hours_total > 0
                else "Privado"
            ),
            inline=True
        )

        embed.add_field(
            name="👥 Grupos",
            value=(
                str(profile.groups_count)
                if profile.groups_count
                else "N/A"
            ),
            inline=True
        )

        emoji, estado = (
            self.estado_steam(
                profile.online_state
            )
        )

        embed.add_field(
            name="📡 Estado",
            value=(
                f"{emoji} {estado}"
            ),
            inline=True
        )

        if profile.location:

            embed.add_field(
                name="🌎 Ubicación",
                value=(
                    profile.location
                ),
                inline=True
            )

        if profile.member_since:

            embed.add_field(
                name="📅 Miembro desde",
                value=(
                    profile.member_since
                ),
                inline=True
            )

        embed.set_footer(
            text="Steam Stats • Datos públicos"
        )

        await interaction.followup.send(
            embed=embed
        )


    # ========================================================
    # /STEAM ID
    # ========================================================

    @steam_group.command(
        name="id",
        description=(
            "Obtiene el SteamID de un perfil."
        )
    )
    @app_commands.describe(
        usuario=(
            "URL o SteamID64."
        )
    )
    async def steam_id(
        self,
        interaction: discord.Interaction,
        usuario: str
    ):

        await interaction.response.defer(
            ephemeral=True
        )

        profile, error = (
            await self.get_profile(
                usuario
            )
        )

        if error:

            await interaction.followup.send(
                f"❌ {error}"
            )

            return

        embed = discord.Embed(
            title="🆔・Steam ID",
            color=PURPLE
        )

        embed.add_field(
            name="Usuario",
            value=(
                profile.nickname
            ),
            inline=True
        )

        embed.add_field(
            name="SteamID64",
            value=(
                f"`{profile.steamid}`"
                if profile.steamid
                else "`No disponible`"
            ),
            inline=True
        )

        embed.add_field(
            name="Perfil",
            value=(
                profile.profile_url
            ),
            inline=False
        )

        await interaction.followup.send(
            embed=embed
        )


    # ========================================================
    # /STEAM LINK
    # ========================================================

    @steam_group.command(
        name="link",
        description=(
            "Genera el enlace al perfil de Steam."
        )
    )
    @app_commands.describe(
        usuario=(
            "SteamID64, URL o nombre personalizado."
        )
    )
    async def steam_link(
        self,
        interaction: discord.Interaction,
        usuario: str
    ):

        perfil = construir_url_perfil(
            usuario
        )

        await interaction.response.send_message(
            f"🎮 **Perfil de Steam:**\n{perfil}"
        )


    # ========================================================
    # ERROR
    # ========================================================

    async def cog_app_command_error(
        self,
        interaction,
        error
    ):

        print(
            "[STEAM] Error:",
            type(error).__name__,
            error
        )

        try:

            mensaje = (
                "❌ No pude obtener la información "
                "de ese perfil de Steam."
            )

            if interaction.response.is_done():

                await interaction.followup.send(
                    mensaje,
                    ephemeral=True
                )

            else:

                await interaction.response.send_message(
                    mensaje,
                    ephemeral=True
                )

        except Exception:

            pass


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Steam(bot)
    )

    print(
        "[STEAM] ✅ Steam Cog instalado."
    )