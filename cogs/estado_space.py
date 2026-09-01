import json
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "estado_space.json"

TEXTO_DETECCION = ".gg/space"


# ============================================================
# BASE DE DATOS JSON
# ============================================================

def cargar_datos():

    DATA_FOLDER.mkdir(
        exist_ok=True
    )

    if not DATA_FILE.exists():

        DATA_FILE.write_text(
            "{}",
            encoding="utf-8"
        )

    try:

        return json.loads(
            DATA_FILE.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return {}


def guardar_datos(data):

    DATA_FOLDER.mkdir(
        exist_ok=True
    )

    DATA_FILE.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# COG
# ============================================================

class EstadoSpace(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.data = cargar_datos()

        # Evita repetir mensajes mientras el usuario
        # mantiene el mismo estado.
        self.detectados = set()

        print(
            "💜 EstadoSpace iniciado."
        )

    # ========================================================
    # OBTENER ESTADO PERSONALIZADO
    # ========================================================

    def obtener_estado(self, member):

        for actividad in member.activities:

            if isinstance(
                actividad,
                discord.CustomActivity
            ):

                nombre = actividad.name or ""

                estado = actividad.state or ""

                texto = (
                    f"{nombre} {estado}"
                ).strip()

                return texto

        return ""

    # ========================================================
    # EVENTO PRESENCE UPDATE
    # ========================================================

    @commands.Cog.listener()
    async def on_presence_update(
        self,
        before,
        after
    ):

        if after.guild is None:

            return

        estado = self.obtener_estado(
            after
        )

        usuario_id = after.id

        # ----------------------------------------------------
        # DETECTAR .GG/SPACE
        # ----------------------------------------------------

        tiene_space = (
            TEXTO_DETECCION.lower()
            in estado.lower()
        )

        # ----------------------------------------------------
        # SI YA NO LO TIENE
        # ----------------------------------------------------

        if not tiene_space:

            self.detectados.discard(
                usuario_id
            )

            return

        # ----------------------------------------------------
        # EVITAR REPETIR
        # ----------------------------------------------------

        if usuario_id in self.detectados:

            return

        self.detectados.add(
            usuario_id
        )

        # ----------------------------------------------------
        # BUSCAR CANAL CONFIGURADO
        # ----------------------------------------------------

        guild_id = str(
            after.guild.id
        )

        configuracion = self.data.get(
            guild_id
        )

        if not configuracion:

            return

        canal_id = configuracion.get(
            "channel_id"
        )

        if not canal_id:

            return

        canal = after.guild.get_channel(
            int(canal_id)
        )

        if canal is None:

            return

        # ----------------------------------------------------
        # MENSAJE
        # ----------------------------------------------------

        embed = discord.Embed(
            description=(
                f"💜 **{after.mention}** "
                f"se puso `{TEXTO_DETECCION}` "
                "en su estado.\n\n"
                "🔥 **¡Sos un máquina!** 🗿"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_footer(
            text="Estado detectado"
        )

        try:

            await canal.send(
                embed=embed
            )

        except discord.Forbidden:

            print(
                f"❌ No tengo permisos para enviar "
                f"mensajes en #{canal.name}."
            )

        except Exception as error:

            print(
                f"❌ Error enviando aviso: {error}"
            )

    # ========================================================
    # /setestadochannel
    # ========================================================

    @app_commands.command(
        name="setestadochannel",
        description="Configura el canal para los avisos de .gg/space."
    )
    @app_commands.describe(
        canal="Canal donde se enviarán los avisos."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def setestadochannel(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona en un servidor.",
                ephemeral=True
            )

        if not interaction.user.guild_permissions.administrator:

            return await interaction.response.send_message(
                "❌ Necesitás permisos de administrador.",
                ephemeral=True
            )

        guild_id = str(
            interaction.guild.id
        )

        self.data[guild_id] = {
            "channel_id": canal.id
        }

        guardar_datos(
            self.data
        )

        await interaction.response.send_message(
            (
                "✅ Canal configurado correctamente.\n\n"
                f"📢 Los avisos de `{TEXTO_DETECCION}` "
                f"se enviarán en {canal.mention}."
            ),
            ephemeral=True
        )

    # ========================================================
    # /estadochannel
    # ========================================================

    @app_commands.command(
        name="estadochannel",
        description="Muestra el canal configurado para los avisos."
    )
    async def estadochannel(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona en un servidor.",
                ephemeral=True
            )

        guild_id = str(
            interaction.guild.id
        )

        configuracion = self.data.get(
            guild_id
        )

        if not configuracion:

            return await interaction.response.send_message(
                "⚠️ Todavía no configuraste ningún canal.",
                ephemeral=True
            )

        canal = interaction.guild.get_channel(
            int(
                configuracion["channel_id"]
            )
        )

        if canal is None:

            return await interaction.response.send_message(
                "⚠️ El canal configurado ya no existe.",
                ephemeral=True
            )

        await interaction.response.send_message(
            (
                "📢 **Canal de avisos**\n\n"
                f"Canal: {canal.mention}\n"
                f"Detectando: `{TEXTO_DETECCION}`"
            ),
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        EstadoSpace(bot)
    )
