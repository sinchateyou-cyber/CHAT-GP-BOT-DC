import discord
from discord.ext import commands
from discord import app_commands
import json
import os
# ============================================================
# CONFIGURACIÓN
# ============================================================
OWNER_FILE = "owner.json"
# ============================================================
# CARGAR OWNER
# ============================================================
def cargar_owner():
    # Si existe owner.json, usar el Owner guardado
    if os.path.exists(OWNER_FILE):
        try:
            with open(OWNER_FILE, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return int(datos["owner_id"])
        except Exception as error:
            print(f"❌ Error leyendo owner.json: {error}")
    # Si no existe owner.json, usar OWNER_ID de config.py
    try:
        from config import OWNER_ID
        return int(OWNER_ID)
    except Exception as error:
        print(f"❌ Error leyendo OWNER_ID: {error}")
        return None
# ============================================================
# GUARDAR OWNER
# ============================================================
def guardar_owner(owner_id):
    datos = {
        "owner_id": str(owner_id)
    }
    with open(OWNER_FILE, "w", encoding="utf-8") as archivo:
        json.dump(
            datos,
            archivo,
            indent=4
        )
# ============================================================
# COG OWNER
# ============================================================
class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.owner_id = cargar_owner()
        print(
            f"👑 Owner configurado: {self.owner_id}"
        )
    # ========================================================
    # COMPROBAR OWNER
    # ========================================================
    def es_owner(self, user_id):
        return user_id == self.owner_id
    # ========================================================
    # /OWNER
    # SOLO EL OWNER PUEDE EJECUTARLO
    # FUNCIONA EN SERVIDOR Y DM
    # ========================================================
    @app_commands.command(
        name="owner",
        description="Muestra quién es el Owner del bot."
    )
    async def owner(
        self,
        interaction: discord.Interaction
    ):
        # Comprobar si es el Owner
        if not self.es_owner(
            interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ No tenés permiso para ejecutar este comando.",
                ephemeral=True
            )
            return
        # Buscar al Owner
        usuario = self.bot.get_user(
            self.owner_id
        )
        # Si el usuario está en caché
        if usuario:
            nombre = usuario.name
            mencion = usuario.mention
        # Si no está en caché
        else:
            try:
                usuario = await self.bot.fetch_user(
                    self.owner_id
                )
                nombre = usuario.name
                mencion = usuario.mention
            except discord.NotFound:
                nombre = "Usuario desconocido"
                mencion = f"<@{self.owner_id}>"
            except discord.HTTPException:
                nombre = "No disponible"
                mencion = f"<@{self.owner_id}>"
        # Crear Embed
        embed = discord.Embed(
            title="👑 Owner del bot",
            description=(
                f"**Owner:** {mencion}\n"
                f"**Usuario:** `{nombre}`\n"
                f"**ID:** `{self.owner_id}`"
            ),
            color=discord.Color.gold()
        )
        embed.set_footer(
            text="Sistema de Owner"
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
    # ========================================================
    # /SETOWNER
    # SOLO EL OWNER ACTUAL PUEDE USARLO
    # ========================================================
    @app_commands.command(
        name="setowner",
        description="Designa a otro usuario como nuevo Owner."
    )
    @app_commands.describe(
        usuario="Usuario que será el nuevo Owner."
    )
    async def setowner(
        self,
        interaction: discord.Interaction,
        usuario: discord.User
    ):
        # Comprobar Owner actual
        if not self.es_owner(
            interaction.user.id
        ):
            await interaction.response.send_message(
                "❌ Solo el Owner actual puede usar este comando.",
                ephemeral=True
            )
            return
        # Evitar cambiarse a sí mismo
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ Ya sos el Owner actual del bot.",
                ephemeral=True
            )
            return
        # Guardar nuevo Owner
        self.owner_id = usuario.id
        guardar_owner(
            usuario.id
        )
        # Crear Embed
        embed = discord.Embed(
            title="👑 Nuevo Owner",
            description=(
                f"{usuario.mention} ahora es el nuevo Owner del bot.\n\n"
                f"**Usuario:** `{usuario.name}`\n"
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
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Owner(bot)
    )