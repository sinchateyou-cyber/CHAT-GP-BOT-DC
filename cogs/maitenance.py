import os
import json
import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# ARCHIVO DE CONFIGURACIÓN
# ============================================================

MAINTENANCE_FILE = "data/maintenance.json"


# ============================================================
# CARGAR ESTADO
# ============================================================

def load_maintenance():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(MAINTENANCE_FILE):
        with open(MAINTENANCE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"enabled": False},
                f,
                indent=4
            )

    try:
        with open(MAINTENANCE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError:
        return {"enabled": False}


# ============================================================
# GUARDAR ESTADO
# ============================================================

def save_maintenance(enabled):
    if not os.path.exists("data"):
        os.makedirs("data")

    with open(MAINTENANCE_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"enabled": enabled},
            f,
            indent=4
        )


# ============================================================
# COG
# ============================================================

class Maintenance(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # GRUPO /MAINTENANCE
    # ========================================================

    maintenance_group = app_commands.Group(
        name="maintenance",
        description="Controla el modo mantenimiento del bot."
    )

    # ========================================================
    # COMPROBAR OWNER
    # ========================================================

    async def is_bot_owner(
        self,
        interaction: discord.Interaction
    ):

        if await self.bot.is_owner(interaction.user):
            return True

        await interaction.response.send_message(
            "❌ Solo el **Owner del bot** puede utilizar este comando.",
            ephemeral=True
        )

        return False

    # ========================================================
    # /MAINTENANCE ON
    # ========================================================

    @maintenance_group.command(
        name="on",
        description="Activa el modo mantenimiento del bot."
    )
    async def maintenance_on(
        self,
        interaction: discord.Interaction
    ):

        if not await self.is_bot_owner(interaction):
            return

        data = load_maintenance()

        if data.get("enabled", False):
            return await interaction.response.send_message(
                "⚠️ El modo mantenimiento ya está activado.",
                ephemeral=True
            )

        save_maintenance(True)

        embed = discord.Embed(
            title="🛠️ Modo mantenimiento activado",
            description=(
                "El bot está ahora en **modo mantenimiento**.\n\n"
                "Los usuarios no podrán utilizar los comandos "
                "que estén configurados para bloquearse durante "
                "el mantenimiento."
            ),
            color=discord.Color.orange()
        )

        embed.add_field(
            name="👑 Owner",
            value=interaction.user.mention,
            inline=True
        )

        embed.add_field(
            name="🔧 Estado",
            value="`MANTENIMIENTO`",
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /MAINTENANCE OFF
    # ========================================================

    @maintenance_group.command(
        name="off",
        description="Desactiva el modo mantenimiento del bot."
    )
    async def maintenance_off(
        self,
        interaction: discord.Interaction
    ):

        if not await self.is_bot_owner(interaction):
            return

        data = load_maintenance()

        if not data.get("enabled", False):
            return await interaction.response.send_message(
                "⚠️ El modo mantenimiento ya está desactivado.",
                ephemeral=True
            )

        save_maintenance(False)

        embed = discord.Embed(
            title="✅ Modo mantenimiento desactivado",
            description=(
                "El bot volvió a estar **activo** y listo "
                "para recibir comandos."
            ),
            color=discord.Color.green()
        )

        embed.add_field(
            name="👑 Owner",
            value=interaction.user.mention,
            inline=True
        )

        embed.add_field(
            name="🟢 Estado",
            value="`ONLINE`",
            inline=True
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # /MAINTENANCE STATUS
    # ========================================================

    @maintenance_group.command(
        name="status",
        description="Muestra el estado actual del modo mantenimiento."
    )
    async def maintenance_status(
        self,
        interaction: discord.Interaction
    ):

        if not await self.is_bot_owner(interaction):
            return

        data = load_maintenance()

        if data.get("enabled", False):

            embed = discord.Embed(
                title="🛠️ Estado del bot",
                description="El modo mantenimiento está **ACTIVADO**.",
                color=discord.Color.orange()
            )

            embed.add_field(
                name="🔧 Estado",
                value="`MANTENIMIENTO`",
                inline=False
            )

        else:

            embed = discord.Embed(
                title="🟢 Estado del bot",
                description="El bot está funcionando normalmente.",
                color=discord.Color.green()
            )

            embed.add_field(
                name="🔧 Estado",
                value="`ONLINE`",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Maintenance(bot))