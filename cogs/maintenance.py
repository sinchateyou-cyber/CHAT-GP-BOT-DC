import discord
from discord.ext import commands
from discord import app_commands
import os
import json

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "maintenance.json")


class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        os.makedirs(DATA_FOLDER, exist_ok=True)

        if not os.path.exists(DATA_FILE):
            self.save_state(False)

        self.maintenance = self.load_state()

    # ============================================================
    # GUARDAR / CARGAR ESTADO
    # ============================================================

    def load_state(self):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("maintenance", False)
        except Exception:
            return False

    def save_state(self, state):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"maintenance": state},
                f,
                indent=4,
                ensure_ascii=False
            )

    # ============================================================
    # /MANTENIMIENTO
    # ============================================================

    @app_commands.command(
        name="mantenimiento",
        description="Activa o desactiva el modo mantenimiento del bot."
    )
    @app_commands.describe(
        estado="Activar o desactivar mantenimiento"
    )
    @app_commands.choices(
        estado=[
            app_commands.Choice(name="🔧 Activar", value="on"),
            app_commands.Choice(name="✅ Desactivar", value="off")
        ]
    )
    async def mantenimiento(
        self,
        interaction: discord.Interaction,
        estado: app_commands.Choice[str]
    ):
        # ========================================================
        # SOLO OWNER DEL SERVIDOR
        # ========================================================

        if not interaction.guild:
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse dentro de un servidor.",
                ephemeral=True
            )
            return

        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Solo el dueño del servidor puede usar este comando.",
                ephemeral=True
            )
            return

        # ========================================================
        # ACTIVAR
        # ========================================================

        if estado.value == "on":

            if self.maintenance:
                await interaction.response.send_message(
                    "🔧 El bot ya está en **mantenimiento**.",
                    ephemeral=True
                )
                return

            self.maintenance = True
            self.save_state(True)

            embed = discord.Embed(
                title="🔧・Mantenimiento activado",
                description=(
                    "El bot entró en **modo mantenimiento**.\n\n"
                    "Durante este período algunas funciones pueden "
                    "permanecer desactivadas."
                ),
                color=discord.Color.orange()
            )

            await interaction.response.send_message(embed=embed)

        # ========================================================
        # DESACTIVAR
        # ========================================================

        else:

            if not self.maintenance:
                await interaction.response.send_message(
                    "✅ El bot ya está funcionando normalmente.",
                    ephemeral=True
                )
                return

            self.maintenance = False
            self.save_state(False)

            embed = discord.Embed(
                title="✅・Mantenimiento finalizado",
                description=(
                    "El bot volvió a estar **activo**.\n\n"
                    "Las funciones pueden utilizarse nuevamente."
                ),
                color=discord.Color.green()
            )

            await interaction.response.send_message(embed=embed)

    # ============================================================
    # FUNCIÓN PARA COMPROBAR MANTENIMIENTO
    # ============================================================

    def is_maintenance(self):
        return self.maintenance


async def setup(bot):
    await bot.add_cog(Maintenance(bot))