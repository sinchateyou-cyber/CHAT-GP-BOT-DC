import os
import json
import discord
from discord.ext import commands
from discord import app_commands


DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "alianza.json")


class Alianza(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.canal_id = self.cargar_canal()

    # ============================================================
    # CARGAR / GUARDAR
    # ============================================================

    def cargar_canal(self):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(DATA_FILE):
            return None

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            return data.get("canal_id")

        except Exception:
            return None

    def guardar_canal(self, canal_id):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"canal_id": canal_id},
                f,
                indent=4
            )

    # ============================================================
    # /setcanalalianza
    # ============================================================

    @app_commands.command(
        name="setcanalalianza",
        description="Establece el canal donde solo se permite /alianza."
    )
    @app_commands.describe(
        canal="Canal donde se permitirán únicamente comandos de alianza."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def setcanalalianza(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        self.canal_id = canal.id
        self.guardar_canal(canal.id)

        await interaction.response.send_message(
            f"✅ Canal configurado correctamente.\n"
            f"📢 Canal: {canal.mention}\n\n"
            f"En este canal se eliminarán automáticamente los mensajes "
            f"que no correspondan al uso de `/alianza`.",
            ephemeral=True
        )

    # ============================================================
    # /desactivarcanalalianza
    # ============================================================

    @app_commands.command(
        name="desactivarcanalalianza",
        description="Desactiva el sistema del canal de alianzas."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def desactivarcanalalianza(
        self,
        interaction: discord.Interaction
    ):

        self.canal_id = None
        self.guardar_canal(None)

        await interaction.response.send_message(
            "✅ Sistema de canal de alianzas desactivado.",
            ephemeral=True
        )

    # ============================================================
    # BORRAR MENSAJES
    # ============================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # Ignorar mensajes del propio bot
        if message.author.bot:
            return

        # Si no hay canal configurado
        if not self.canal_id:
            return

        # Si no es el canal configurado
        if message.channel.id != self.canal_id:
            return

        # --------------------------------------------------------
        # Borrar cualquier mensaje escrito
        # --------------------------------------------------------

        try:
            await message.delete()

        except discord.NotFound:
            pass

        except discord.Forbidden:
            print(
                "❌ No tengo permiso para borrar mensajes "
                f"en #{message.channel.name}"
            )

        except Exception as e:
            print(f"❌ Error eliminando mensaje: {e}")


# ================================================================
# SETUP
# ================================================================

async def setup(bot):
    await bot.add_cog(Alianza(bot))