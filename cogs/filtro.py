import discord
from discord.ext import commands
import re


# ============================================================
# CONFIGURACIÓN
# ============================================================

PALABRAS_PROHIBIDAS = {
    "puto",
    "puta",
    "putita",
    "putito",
    "pajero",
    "pajera",
    "pajear",
    "pelotudo",
    "pelotuda",
    "boludo",
    "boluda",
    "forro",
    "forra",
    "forrito",
    "mierda",
    "concha",
    "conchudo",
    "conchuda",
    "verga",
    "vergudo",
    "culo",
    "culiado",
    "culiada",
    "hdp",
    "hdp",
    "hijoputa",
    "hijo de puta",
    "malparido",
    "malparida",
    "gilipollas",
    "idiota",
    "imbecil",
    "imbécil",
}


# ============================================================
# NORMALIZAR TEXTO
# ============================================================

def normalizar_texto(texto: str) -> str:

    texto = texto.lower()

    reemplazos = {
        "0": "o",
        "1": "i",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    # Elimina símbolos para detectar cosas como:
    # p.u.t.a
    # p-u-t-o
    # p_u_t_a

    texto = re.sub(
        r"[\W_]+",
        " ",
        texto,
        flags=re.UNICODE
    )

    return texto


# ============================================================
# DETECTAR PALABRA
# ============================================================

def encontrar_palabra_prohibida(
    texto: str
):

    texto_normalizado = normalizar_texto(
        texto
    )

    for palabra in PALABRAS_PROHIBIDAS:

        palabra_normalizada = normalizar_texto(
            palabra
        )

        patron = (
            r"(?<!\w)"
            + re.escape(palabra_normalizada)
            + r"(?!\w)"
        )

        if re.search(
            patron,
            texto_normalizado,
            flags=re.IGNORECASE
        ):
            return palabra

    return None


# ============================================================
# COG FILTRO
# ============================================================

class Filtro(commands.Cog):

    def __init__(
        self,
        bot
    ):
        self.bot = bot

        print(
            "🛡️ Filtro de mensajes cargado."
        )

    # ========================================================
    # MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(
        self,
        message: discord.Message
    ):

        # Ignorar bots

        if message.author.bot:
            return

        # Ignorar mensajes sin contenido

        if not message.content:
            return

        palabra = encontrar_palabra_prohibida(
            message.content
        )

        if palabra is None:

            return

        # ====================================================
        # BORRAR MENSAJE
        # ====================================================

        try:

            await message.delete()

            print(
                f"🗑️ Mensaje eliminado | "
                f"Usuario: {message.author} | "
                f"Servidor: {message.guild} | "
                f"Palabra: {palabra}"
            )

        except discord.Forbidden:

            print(
                "❌ No tengo permiso para eliminar "
                "mensajes en este canal."
            )

            return

        except discord.NotFound:

            return

        except Exception as error:

            print(
                f"❌ Error eliminando mensaje: {error}"
            )

            return

        # ====================================================
        # MANDAR DM
        # ====================================================

        try:

            embed = discord.Embed(
                title="⚠️ Mensaje eliminado",
                description=(
                    "Tu mensaje fue eliminado automáticamente "
                    "porque contenía lenguaje no permitido."
                ),
                color=discord.Color.red()
            )

            if message.guild:

                embed.add_field(
                    name="Servidor",
                    value=message.guild.name,
                    inline=False
                )

            embed.add_field(
                name="Motivo",
                value=(
                    "Uso de lenguaje malsonante."
                ),
                inline=False
            )

            embed.set_footer(
                text="Sistema automático de moderación"
            )

            await message.author.send(
                embed=embed
            )

            print(
                f"📩 DM enviado a {message.author}"
            )

        except discord.Forbidden:

            print(
                f"⚠️ No se pudo enviar DM a "
                f"{message.author} "
                f"(DMs cerrados)."
            )

        except Exception as error:

            print(
                f"❌ Error enviando DM: {error}"
            )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):
    await bot.add_cog(
        Filtro(bot)
    )

    print(
        "✅ Cog Filtro cargado correctamente."
    )