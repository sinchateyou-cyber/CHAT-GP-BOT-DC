import os
import json
import discord
from discord.ext import commands
from discord import app_commands


DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "canal_confesiones.json")


class CanalConfesiones(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.canal_id = self.cargar_canal()

    # ============================================================
    # CARGAR CONFIGURACIÓN
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

    # ============================================================
    # GUARDAR CONFIGURACIÓN
    # ============================================================

    def guardar_canal(self, canal_id):
        os.makedirs(DATA_FOLDER, exist_ok=True)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"canal_id": canal_id},
                f,
                indent=4
            )

    # ============================================================
    # /setcanalconfesiones
    # ============================================================

    @app_commands.command(
        name="setcanalconfesiones",
        description="Configura el canal exclusivo para confesiones."
    )
    @app_commands.describe(
        canal="Canal donde solamente se permitirá /confesar."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setcanalconfesiones(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        self.canal_id = canal.id
        self.guardar_canal(canal.id)

        await interaction.response.send_message(
            f"✅ Canal de confesiones configurado: {canal.mention}\n\n"
            "💌 En este canal se eliminarán automáticamente "
            "los mensajes que no sean `/confesar`.",
            ephemeral=True
        )

    # ============================================================
    # /desactivarcanalconfesiones
    # ============================================================

    @app_commands.command(
        name="desactivarcanalconfesiones",
        description="Desactiva el canal exclusivo de confesiones."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def desactivarcanalconfesiones(
        self,
        interaction: discord.Interaction
    ):

        self.canal_id = None
        self.guardar_canal(None)

        await interaction.response.send_message(
            "✅ Canal exclusivo de confesiones desactivado.",
            ephemeral=True
        )

    # ============================================================
    # ELIMINAR MENSAJES
    # ============================================================

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        # Ignorar bots
        if message.author.bot:
            return

        # Si no hay canal configurado
        if not self.canal_id:
            return

        # Si no es el canal de confesiones
        if message.channel.id != self.canal_id:
            return

        # ========================================================
        # BORRAR TODO MENSAJE NORMAL
        # ========================================================

        try:
            await message.delete()

        except discord.NotFound:
            pass

        except discord.Forbidden:
            print(
                f"❌ No tengo permiso para borrar mensajes "
                f"en #{message.channel.name}"
            )

        except Exception as e:
            print(
                f"❌ Error eliminando mensaje: {e}"
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(CanalConfesiones(bot))