import json
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "canales_permitidos.json"


# ============================================================
# DATOS
# ============================================================

def cargar_datos():
    DATA_FOLDER.mkdir(exist_ok=True)

    if not DATA_FILE.exists():
        try:
            DATA_FILE.write_text(
                "{}",
                encoding="utf-8"
            )
        except Exception as e:
            print(f"❌ No se pudo crear el archivo de datos: {e}")
            return {}

    try:
        data = json.loads(
            DATA_FILE.read_text(
                encoding="utf-8"
            )
        )

        if isinstance(data, dict):
            return data

        return {}

    except Exception as e:
        print(
            f"❌ Error leyendo canales_permitidos.json: {e}"
        )
        return {}


def guardar_datos(data):
    DATA_FOLDER.mkdir(exist_ok=True)

    try:
        DATA_FILE.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    except Exception as e:
        print(
            f"❌ Error guardando canales_permitidos.json: {e}"
        )


# ============================================================
# COG
# ============================================================

class CanalPermitido(commands.Cog):

    def __init__(self, bot: commands.Bot):

        self.bot = bot

        # ====================================================
        # CARGAR CONFIGURACIÓN
        # ====================================================

        self.data = cargar_datos()

        print(
            f"✅ CanalPermitido cargado. "
            f"{len(self.data)} canal(es) configurado(s)."
        )

    # ========================================================
    # EVENTO DE MENSAJES
    # ========================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # ====================================================
        # IGNORAR MENSAJES DEL BOT
        # ====================================================

        if message.author.bot:
            return

        # ====================================================
        # IGNORAR DMs
        # ====================================================

        if message.guild is None:
            return

        # ====================================================
        # BUSCAR CONFIGURACIÓN DEL CANAL
        # ====================================================

        channel_id = str(message.channel.id)

        configuracion = self.data.get(channel_id)

        # Si el canal no está configurado, no hacemos nada
        if not configuracion:
            return

        # ====================================================
        # ADMINISTRADORES
        # ====================================================
        # Los administradores pueden escribir normalmente.
        # Esto evita que el dueño/moderadores queden bloqueados.
        # ====================================================

        if message.author.guild_permissions.administrator:
            return

        # ====================================================
        # MENSAJE PERMITIDO
        # ====================================================

        mensaje_permitido = configuracion.get(
            "mensaje",
            ""
        )

        # ====================================================
        # COMPARAR MENSAJE
        # ====================================================

        if message.content.strip().lower() == mensaje_permitido.strip().lower():

            return

        # ====================================================
        # BORRAR MENSAJE
        # ====================================================

        try:

            await message.delete()

        except discord.NotFound:
            # Ya fue eliminado.
            pass

        except discord.Forbidden:

            print(
                f"❌ No tengo permisos para borrar mensajes "
                f"en #{message.channel.name} "
                f"({message.guild.name})."
            )

        except discord.HTTPException as e:

            print(
                f"❌ Error borrando mensaje en "
                f"#{message.channel.name}: {e}"
            )

        except Exception as e:

            print(
                f"❌ Error inesperado borrando mensaje: {e}"
            )

    # ========================================================
    # /CANALPERMITIDO
    # ========================================================

    @app_commands.command(
        name="canalpermitido",
        description=(
            "Configura un canal donde solo se permite un mensaje determinado."
        )
    )
    @app_commands.describe(
        canal="Canal donde se aplicará la restricción.",
        mensaje="Mensaje exacto que estará permitido enviar."
    )
    @app_commands.default_permissions(
        manage_channels=True
    )
    async def canalpermitido(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel,
        mensaje: str
    ):

        # ====================================================
        # SERVIDOR
        # ====================================================

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ====================================================
        # PERMISOS
        # ====================================================

        if not interaction.user.guild_permissions.manage_channels:

            return await interaction.response.send_message(
                "❌ Necesitás el permiso **Gestionar canales**.",
                ephemeral=True
            )

        # ====================================================
        # VALIDAR MENSAJE
        # ====================================================

        mensaje = mensaje.strip()

        if not mensaje:

            return await interaction.response.send_message(
                "❌ Tenés que indicar un mensaje permitido.",
                ephemeral=True
            )

        # ====================================================
        # GUARDAR CONFIGURACIÓN
        # ====================================================

        self.data[str(canal.id)] = {
            "guild_id": interaction.guild.id,
            "channel_id": canal.id,
            "mensaje": mensaje
        }

        guardar_datos(
            self.data
        )

        # ====================================================
        # RESPUESTA
        # ====================================================

        await interaction.response.send_message(
            "✅ **Canal configurado correctamente.**\n\n"
            f"📌 Canal: {canal.mention}\n"
            f"💬 Mensaje permitido: `{mensaje}`\n\n"
            "🗑️ Cualquier otro mensaje será eliminado automáticamente.\n"
            "💾 La configuración quedará guardada aunque reinicies el bot.",
            ephemeral=True
        )

        print(
            f"✅ Canal permitido configurado: "
            f"{canal.id} | "
            f"Mensaje: {mensaje}"
        )

    # ========================================================
    # /QUITARCANALPERMITIDO
    # ========================================================

    @app_commands.command(
        name="quitarcanalpermitido",
        description=(
            "Desactiva la restricción de un canal."
        )
    )
    @app_commands.describe(
        canal="Canal al que querés quitarle la restricción."
    )
    @app_commands.default_permissions(
        manage_channels=True
    )
    async def quitarcanalpermitido(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        # ====================================================
        # SERVIDOR
        # ====================================================

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ====================================================
        # PERMISOS
        # ====================================================

        if not interaction.user.guild_permissions.manage_channels:

            return await interaction.response.send_message(
                "❌ Necesitás el permiso **Gestionar canales**.",
                ephemeral=True
            )

        # ====================================================
        # COMPROBAR CONFIGURACIÓN
        # ====================================================

        channel_id = str(canal.id)

        if channel_id not in self.data:

            return await interaction.response.send_message(
                f"❌ {canal.mention} no tiene ninguna restricción configurada.",
                ephemeral=True
            )

        # ====================================================
        # ELIMINAR
        # ====================================================

        del self.data[channel_id]

        guardar_datos(
            self.data
        )

        # ====================================================
        # RESPUESTA
        # ====================================================

        await interaction.response.send_message(
            f"✅ Se quitó la restricción de {canal.mention}.\n\n"
            "💬 Ahora se pueden enviar mensajes normalmente en ese canal.",
            ephemeral=True
        )

        print(
            f"🗑️ Restricción eliminada del canal {canal.id}"
        )

    # ========================================================
    # /VERCANALESPERMITIDOS
    # ========================================================

    @app_commands.command(
        name="vercanalespermitidos",
        description=(
            "Muestra los canales que tienen una restricción activa."
        )
    )
    @app_commands.default_permissions(
        manage_channels=True
    )
    async def vercanalespermitidos(
        self,
        interaction: discord.Interaction
    ):

        # ====================================================
        # SERVIDOR
        # ====================================================

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ====================================================
        # PERMISOS
        # ====================================================

        if not interaction.user.guild_permissions.manage_channels:

            return await interaction.response.send_message(
                "❌ Necesitás el permiso **Gestionar canales**.",
                ephemeral=True
            )

        # ====================================================
        # BUSCAR CANALES DEL SERVIDOR
        # ====================================================

        canales_servidor = []

        for channel_id, configuracion in self.data.items():

            try:

                guild_id = int(
                    configuracion.get(
                        "guild_id",
                        0
                    )
                )

                if guild_id != interaction.guild.id:
                    continue

                canal_id = int(channel_id)

                canal = interaction.guild.get_channel(
                    canal_id
                )

                if canal is None:
                    continue

                mensaje = configuracion.get(
                    "mensaje",
                    ""
                )

                canales_servidor.append(
                    (
                        canal,
                        mensaje
                    )
                )

            except Exception:
                continue

        # ====================================================
        # NO HAY CANALES
        # ====================================================

        if not canales_servidor:

            return await interaction.response.send_message(
                "ℹ️ Este servidor no tiene ningún canal configurado.",
                ephemeral=True
            )

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="💜 Canales permitidos",
            description=(
                "Estos son los canales que tienen "
                "restricción de mensajes."
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        for canal, mensaje in canales_servidor:

            embed.add_field(
                name=f"📌 {canal.name}",
                value=(
                    f"Canal: {canal.mention}\n"
                    f"💬 Permitido: `{mensaje}`"
                ),
                inline=False
            )

        embed.set_footer(
            text=(
                f"{len(canales_servidor)} "
                f"canal(es) configurado(s)"
            )
        )

        # ====================================================
        # ENVIAR
        # ====================================================

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot: commands.Bot
):

    await bot.add_cog(
        CanalPermitido(bot)
    )