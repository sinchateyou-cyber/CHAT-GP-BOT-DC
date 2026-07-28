import discord
from discord.ext import commands
from discord import app_commands
import json
import os
# ============================================================
# ARCHIVO DONDE SE GUARDA EL OWNER
# ============================================================
OWNER_FILE = "owner.json"
# ============================================================
# CARGAR OWNER
# ============================================================
def cargar_owner():
    # Si no existe owner.json, usa el OWNER_ID de config.py
    if not os.path.exists(OWNER_FILE):
        try:
            from config import OWNER_ID
            return int(OWNER_ID)
        except Exception:
            return None
    try:
        with open(OWNER_FILE, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return int(datos["owner_id"])
    except Exception:
        try:
            from config import OWNER_ID
            return int(OWNER_ID)
        except Exception:
            return None
# ============================================================
# GUARDAR OWNER
# ============================================================
def guardar_owner(owner_id):
    datos = {
        "owner_id": str(owner_id)
    }
    with open(OWNER_FILE, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, indent=4)
# ============================================================
# COG OWNER
# ============================================================
class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = cargar_owner()
    # ========================================================
    # COMANDO /SETOWNER
    # ========================================================
    @app_commands.command(
        name="setowner",
        description="Designa a otro usuario como Owner del bot."
    )
    @app_commands.describe(
        usuario="Usuario que será el nuevo Owner del bot."
    )
    async def setowner(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):
        # Verificar que el comando tenga un Owner configurado
        if self.owner_id is None:
            await interaction.response.send_message(
                "❌ No hay un Owner configurado.",
                ephemeral=True
            )
            return
        # Verificar que quien ejecuta el comando sea el Owner actual
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(
                "❌ Solo el Owner actual puede designar a otro Owner.",
                ephemeral=True
            )
            return
        # Evitar designarse a sí mismo
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ Ya sos el Owner actual del bot.",
                ephemeral=True
            )
            return
        # Guardar nuevo Owner
        self.owner_id = usuario.id
        guardar_owner(usuario.id)
        # Embed de confirmación
        embed = discord.Embed(
            title="👑 Nuevo Owner designado",
            description=(
                f"{usuario.mention} ahora es el nuevo Owner del bot.\n\n"
                f"**ID:** `{usuario.id}`"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(
            text=f"Designado por {interaction.user}"
        )
        await interaction.response.send_message(
            embed=embed
        )
    # ========================================================
    # COMANDO /OWNER
    # ========================================================
    @app_commands.command(
        name="owner",
        description="Muestra quién es el Owner actual del bot."
    )
    async def owner(
        self,
        interaction: discord.Interaction
    ):
        if self.owner_id is None:
            await interaction.response.send_message(
                "❌ No hay un Owner configurado.",
                ephemeral=True
            )
            return
        usuario = self.bot.get_user(self.owner_id)
        if usuario:
            nombre = usuario.mention
        else:
            nombre = f"<@{self.owner_id}>"
        embed = discord.Embed(
            title="👑 Owner del bot",
            description=(
                f"El Owner actual es {nombre}\n\n"
                f"**ID:** `{self.owner_id}`"
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(
            embed=embed
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(Owner(bot))