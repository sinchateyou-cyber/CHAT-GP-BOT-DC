import random
import re
import requests

import discord
from discord.ext import commands
from discord import app_commands

from bs4 import BeautifulSoup


# ============================================================
# CONFIGURACIÓN
# ============================================================

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/18.0 Mobile/15E148 Safari/604.1"
    ),
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}

TIMEOUT = 10


# ============================================================
# BUSCAR EN PINTEREST
# ============================================================

def buscar_pinterest(consulta: str):

    consulta = consulta.strip()

    if not consulta:
        return []

    url = (
        "https://www.pinterest.com/search/pins/"
        "?q="
        + requests.utils.quote(consulta)
    )

    try:

        respuesta = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if respuesta.status_code != 200:
            print(
                f"❌ Pinterest respondió "
                f"{respuesta.status_code}"
            )
            return []

        html = respuesta.text

    except requests.RequestException as error:

        print(
            f"❌ Error conectando con Pinterest: {error}"
        )

        return []

    resultados = []

    # --------------------------------------------------------
    # BUSCAR URLs DE IMÁGENES
    # --------------------------------------------------------

    patrones = [

        r'https://i\.pinimg\.com/[^"\\]+',

        r'https:\\/\\/i\.pinimg\.com\\/[^"\\]+',

    ]

    for patron in patrones:

        encontrados = re.findall(
            patron,
            html
        )

        for imagen in encontrados:

            imagen = imagen.replace(
                "\\/",
                "/"
            )

            imagen = imagen.replace(
                "\\u002F",
                "/"
            )

            imagen = imagen.replace(
                "\\u0026",
                "&"
            )

            # Limpiar caracteres HTML
            imagen = imagen.split('"')[0]
            imagen = imagen.split("\\")[0]

            if (
                imagen.startswith(
                    "https://i.pinimg.com/"
                )
                and imagen not in resultados
            ):

                resultados.append(
                    imagen
                )

    # --------------------------------------------------------
    # EXTRAER TAMBIÉN OG IMAGE
    # --------------------------------------------------------

    try:

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for meta in soup.find_all(
            "meta"
        ):

            contenido = meta.get(
                "content"
            )

            if not contenido:
                continue

            if (
                "i.pinimg.com"
                in contenido
            ):

                if contenido not in resultados:

                    resultados.append(
                        contenido
                    )

    except Exception as error:

        print(
            f"⚠️ Error procesando HTML: {error}"
        )

    return resultados


# ============================================================
# COG
# ============================================================

class Pinterest(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print(
            "📌 Pinterest iniciado."
        )

    # ========================================================
    # /banner
    # ========================================================

    @app_commands.command(
        name="banner",
        description="Busca un banner en Pinterest."
    )
    @app_commands.describe(
        busqueda="Qué tipo de banner querés buscar."
    )
    async def banner(
        self,
        interaction: discord.Interaction,
        busqueda: str
    ):

        await interaction.response.defer()

        consulta = (
            f"{busqueda} banner discord"
        )

        imagenes = buscar_pinterest(
            consulta
        )

        if not imagenes:

            return await interaction.followup.send(
                "❌ No encontré banners en Pinterest."
            )

        imagen = random.choice(
            imagenes
        )

        embed = discord.Embed(
            title="🖼️ Banner encontrado",
            description=(
                f"🔎 **Búsqueda:** `{busqueda}`\n\n"
                "📌 Encontrado en Pinterest."
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_image(
            url=imagen
        )

        embed.set_footer(
            text="Pinterest • Búsqueda pública"
        )

        await interaction.followup.send(
            embed=embed
        )

    # ========================================================
    # /pfp
    # ========================================================

    @app_commands.command(
        name="pfp",
        description="Busca una foto de perfil en Pinterest."
    )
    @app_commands.describe(
        busqueda="Qué tipo de foto de perfil querés buscar."
    )
    async def pfp(
        self,
        interaction: discord.Interaction,
        busqueda: str
    ):

        await interaction.response.defer()

        consulta = (
            f"{busqueda} pfp profile picture"
        )

        imagenes = buscar_pinterest(
            consulta
        )

        if not imagenes:

            return await interaction.followup.send(
                "❌ No encontré fotos de perfil en Pinterest."
            )

        imagen = random.choice(
            imagenes
        )

        embed = discord.Embed(
            title="👤 PFP encontrada",
            description=(
                f"🔎 **Búsqueda:** `{busqueda}`\n\n"
                "📌 Encontrada en Pinterest."
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_image(
            url=imagen
        )

        embed.set_footer(
            text="Pinterest • Búsqueda pública"
        )

        await interaction.followup.send(
            embed=embed
        )

    # ========================================================
    # /banner_random
    # ========================================================

    @app_commands.command(
        name="banner_random",
        description="Busca un banner aleatorio en Pinterest."
    )
    async def banner_random(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer()

        consultas = [
            "discord banner aesthetic",
            "discord banner gaming",
            "discord banner purple",
            "discord banner black",
            "discord banner anime",
            "discord banner free fire",
            "discord banner boy",
            "discord banner girl",
        ]

        consulta = random.choice(
            consultas
        )

        imagenes = buscar_pinterest(
            consulta
        )

        if not imagenes:

            return await interaction.followup.send(
                "❌ No pude encontrar un banner."
            )

        imagen = random.choice(
            imagenes
        )

        embed = discord.Embed(
            title="🎲 Banner aleatorio",
            description=(
                "Encontré este banner buscando "
                f"`{consulta}` en Pinterest."
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_image(
            url=imagen
        )

        embed.set_footer(
            text="Pinterest • Aleatorio"
        )

        await interaction.followup.send(
            embed=embed
        )

    # ========================================================
    # /pfp_random
    # ========================================================

    @app_commands.command(
        name="pfp_random",
        description="Busca una PFP aleatoria en Pinterest."
    )
    async def pfp_random(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer()

        consultas = [
            "pfp aesthetic",
            "pfp anime",
            "pfp gaming",
            "pfp purple",
            "pfp black",
            "pfp boy",
            "pfp girl",
            "pfp dark",
        ]

        consulta = random.choice(
            consultas
        )

        imagenes = buscar_pinterest(
            consulta
        )

        if not imagenes:

            return await interaction.followup.send(
                "❌ No pude encontrar una PFP."
            )

        imagen = random.choice(
            imagenes
        )

        embed = discord.Embed(
            title="🎲 PFP aleatoria",
            description=(
                "Encontré esta PFP buscando "
                f"`{consulta}` en Pinterest."
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_image(
            url=imagen
        )

        embed.set_footer(
            text="Pinterest • Aleatorio"
        )

        await interaction.followup.send(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Pinterest(bot)
    )