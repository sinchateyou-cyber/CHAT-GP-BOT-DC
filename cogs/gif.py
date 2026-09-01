
import io
import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image


# ============================================================
# CONFIGURACIÓN
# ============================================================

ANCHO = 500
ALTO = 500

FRAMES = 24
DURACION_FRAME = 70


# ============================================================
# COG
# ============================================================

class Gif(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        print("🎞️ Gif iniciado.")

    # ========================================================
    # /gif
    # ========================================================

    @app_commands.command(
        name="gif",
        description="Convierte una imagen en un GIF animado."
    )
    @app_commands.describe(
        imagen="Imagen que querés convertir en GIF."
    )
    async def gif(
        self,
        interaction: discord.Interaction,
        imagen: discord.Attachment
    ):

        await interaction.response.defer()

        # ----------------------------------------------------
        # COMPROBAR FORMATO
        # ----------------------------------------------------

        if not imagen.content_type:

            return await interaction.followup.send(
                "❌ No pude detectar el tipo de archivo."
            )

        if not imagen.content_type.startswith(
            "image/"
        ):

            return await interaction.followup.send(
                "❌ El archivo tiene que ser una imagen."
            )

        # ----------------------------------------------------
        # DESCARGAR IMAGEN
        # ----------------------------------------------------

        try:

            datos = await imagen.read()

        except Exception as error:

            print(
                f"❌ Error descargando imagen: {error}"
            )

            return await interaction.followup.send(
                "❌ No pude descargar la imagen."
            )

        # ----------------------------------------------------
        # ABRIR IMAGEN
        # ----------------------------------------------------

        try:

            original = Image.open(
                io.BytesIO(datos)
            ).convert(
                "RGBA"
            )

        except Exception as error:

            print(
                f"❌ Error abriendo imagen: {error}"
            )

            return await interaction.followup.send(
                "❌ Esa imagen no es válida."
            )

        # ----------------------------------------------------
        # CREAR FRAMES
        # ----------------------------------------------------

        frames = []

        ancho_original, alto_original = (
            original.size
        )

        lado = min(
            ancho_original,
            alto_original
        )

        izquierda = (
            ancho_original - lado
        ) // 2

        arriba = (
            alto_original - lado
        ) // 2

        recorte = original.crop(
            (
                izquierda,
                arriba,
                izquierda + lado,
                arriba + lado
            )
        )

        for i in range(FRAMES):

            # Zoom suave de ida y vuelta
            progreso = i / (FRAMES - 1)

            zoom = 1 + (
                0.08
                * (
                    1
                    - abs(
                        2 * progreso - 1
                    )
                )
            )

            tamaño = int(
                lado * zoom
            )

            frame = recorte.resize(
                (
                    tamaño,
                    tamaño
                ),
                Image.Resampling.LANCZOS
            )

            izquierda_frame = (
                tamaño - lado
            ) // 2

            arriba_frame = (
                tamaño - lado
            ) // 2

            frame = frame.crop(
                (
                    izquierda_frame,
                    arriba_frame,
                    izquierda_frame + lado,
                    arriba_frame + lado
                )
            )

            frame = frame.resize(
                (
                    ANCHO,
                    ALTO
                ),
                Image.Resampling.LANCZOS
            )

            frames.append(
                frame.convert(
                    "P",
                    palette=Image.Palette.ADAPTIVE
                )
            )

        # ----------------------------------------------------
        # GUARDAR GIF
        # ----------------------------------------------------

        salida = io.BytesIO()

        try:

            frames[0].save(
                salida,
                format="GIF",
                save_all=True,
                append_images=frames[1:],
                duration=DURACION_FRAME,
                loop=0,
                optimize=True
            )

        except Exception as error:

            print(
                f"❌ Error creando GIF: {error}"
            )

            return await interaction.followup.send(
                "❌ No pude crear el GIF."
            )

        salida.seek(0)

        # ----------------------------------------------------
        # ENVIAR
        # ----------------------------------------------------

        archivo = discord.File(
            salida,
            filename="gif.gif"
        )

        embed = discord.Embed(
            title="🎞️ GIF creado",
            description=(
                f"✨ **Listo, {interaction.user.mention}!**\n"
                "Convertí tu imagen en un GIF animado."
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_footer(
            text="GIF Generator"
        )

        await interaction.followup.send(
            embed=embed,
            file=archivo
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        Gif(bot)
    )
