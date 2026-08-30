import os
import json
import discord
from discord.ext import commands
from discord import app_commands


DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "confesiones.json")


# ============================================================
# UTILIDADES
# ============================================================

def cargar_config():
    os.makedirs(DATA_FOLDER, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_config(data):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# ============================================================
# MODAL DE CONFESIÓN
# ============================================================

class ConfesionModal(discord.ui.Modal, title="💌 Nueva confesión"):

    confesion = discord.ui.TextInput(
        label="Tu confesión",
        placeholder="Escribí tu confesión acá...",
        style=discord.TextStyle.paragraph,
        min_length=1,
        max_length=2000,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        cog = interaction.client.get_cog("Confesiones")

        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema de confesiones no está disponible.",
                ephemeral=True
            )

        canal_id = cog.config.get("canal_id")

        if not canal_id:
            return await interaction.response.send_message(
                "❌ El sistema de confesiones todavía no está configurado.",
                ephemeral=True
            )

        canal = interaction.guild.get_channel(canal_id)

        if canal is None:
            return await interaction.response.send_message(
                "❌ No encontré el canal configurado para las confesiones.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="💌 Confesión anónima",
            description=str(self.confesion.value),
            color=discord.Color.purple()
        )

        embed.set_footer(
            text="Confesión anónima • Nadie puede ver quién la envió"
        )

        try:
            await canal.send(embed=embed)

            await interaction.response.send_message(
                "✅ Tu confesión fue enviada de forma anónima.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para enviar mensajes en ese canal.",
                ephemeral=True
            )

        except Exception as e:
            print(f"[CONFESIONES] Error: {e}")

            await interaction.response.send_message(
                "❌ Ocurrió un error al enviar la confesión.",
                ephemeral=True
            )


# ============================================================
# COG
# ============================================================

class Confesiones(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.config = cargar_config()

    # ========================================================
    # /confesar
    # ========================================================

    @app_commands.command(
        name="confesar",
        description="Envía una confesión anónima."
    )
    async def confesar(self, interaction: discord.Interaction):

        canal_id = self.config.get("canal_id")

        if not canal_id:
            return await interaction.response.send_message(
                "❌ El sistema de confesiones no está configurado.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            ConfesionModal()
        )

    # ========================================================
    # /setconfesiones
    # ========================================================

    @app_commands.command(
        name="setconfesiones",
        description="Configura el canal de confesiones."
    )
    @app_commands.describe(
        canal="Canal donde aparecerán las confesiones."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setconfesiones(
        self,
        interaction: discord.Interaction,
        canal: discord.TextChannel
    ):

        self.config["canal_id"] = canal.id
        guardar_config(self.config)

        await interaction.response.send_message(
            f"✅ Canal de confesiones configurado en {canal.mention}.",
            ephemeral=True
        )

    # ========================================================
    # /desactivarconfesiones
    # ========================================================

    @app_commands.command(
        name="desactivarconfesiones",
        description="Desactiva el sistema de confesiones."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def desactivarconfesiones(
        self,
        interaction: discord.Interaction
    ):

        self.config["canal_id"] = None
        guardar_config(self.config)

        await interaction.response.send_message(
            "✅ Sistema de confesiones desactivado.",
            ephemeral=True
        )

    # ========================================================
    # ERROR DE PERMISOS
    # ========================================================

    @setconfesiones.error
    @desactivarconfesiones.error
    async def permisos_error(
        self,
        interaction: discord.Interaction,
        error
    ):

        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitás el permiso **Gestionar servidor**.",
                ephemeral=True
            )
            return

        print(f"[CONFESIONES] Error de comando: {error}")


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Confesiones(bot))