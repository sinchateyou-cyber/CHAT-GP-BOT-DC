import discord
from discord.ext import commands
import os
import json

# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLES_FILE = "data/roles.json"

EDADES = {
    "14-16": "14-16",
    "16-18": "16-18",
    "18-25": "18-25",
}


# ============================================================
# FUNCIONES
# ============================================================

def cargar_roles():
    if not os.path.exists(ROLES_FILE):
        return {}

    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_roles(data):
    os.makedirs("data", exist_ok=True)

    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ============================================================
# BOTONES
# ============================================================

class EdadButton(discord.ui.Button):

    def __init__(self, edad):
        super().__init__(
            label=edad,
            style=discord.ButtonStyle.secondary,
            custom_id=f"edad_{edad.replace('-', '_')}"
        )

        self.edad = edad

    async def callback(self, interaction: discord.Interaction):

        guild = interaction.guild

        if guild is None:
            return await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # BUSCAR ROL ELEGIDO
        # ----------------------------------------------------

        rol_elegido = discord.utils.get(
            guild.roles,
            name=self.edad
        )

        if rol_elegido is None:
            return await interaction.response.send_message(
                f"❌ No encontré el rol `{self.edad}`.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # BUSCAR TODOS LOS ROLES DE EDAD
        # ----------------------------------------------------

        roles_edad = []

        for nombre in EDADES.values():
            rol = discord.utils.get(guild.roles, name=nombre)

            if rol:
                roles_edad.append(rol)

        # ----------------------------------------------------
        # QUITAR ROLES ANTERIORES
        # ----------------------------------------------------

        quitar = [
            rol for rol in roles_edad
            if rol in interaction.user.roles and rol != rol_elegido
        ]

        if quitar:
            try:
                await interaction.user.remove_roles(*quitar)
            except discord.Forbidden:
                return await interaction.response.send_message(
                    "❌ No puedo quitar tus roles de edad. "
                    "Revisá que mi rol esté por encima de esos roles.",
                    ephemeral=True
                )

        # ----------------------------------------------------
        # SI YA TIENE EL ROL
        # ----------------------------------------------------

        if rol_elegido in interaction.user.roles:

            return await interaction.response.send_message(
                f"🎀 Ya tenés seleccionado el rol **{self.edad}**.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # DAR ROL
        # ----------------------------------------------------

        try:
            await interaction.user.add_roles(rol_elegido)

        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No puedo darte ese rol.\n\n"
                "Asegurate de que mi rol esté **por encima** "
                "de los roles de edad.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # CONFIRMACIÓN
        # ----------------------------------------------------

        await interaction.response.send_message(
            f"🎀 Listo, se te asignó el rol **{self.edad}**.",
            ephemeral=True
        )


# ============================================================
# PANEL
# ============================================================

class EdadView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        for edad in EDADES:
            self.add_item(EdadButton(edad))


# ============================================================
# COG
# ============================================================

class Edad(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # /edad
    # ========================================================

    @commands.hybrid_command(
        name="edad",
        description="Envía el panel para seleccionar tu edad."
    )
    @commands.has_permissions(administrator=True)
    async def edad(self, ctx):

        embed = discord.Embed(
            title="🎀・selecciona tu edad",
            description=(
                "**Elegí tu rango de edad:**\n\n"
                "🎀 **14-16**\n"
                "🎀 **16-18**\n"
                "🎀 **18-25**\n\n"
                "*Se honesto porfavor.* ♡"
            ),
            color=discord.Color.from_rgb(148, 0, 211)
        )

        embed.set_footer(
            text="Seleccioná una opción para obtener tu rol."
        )

        await ctx.send(
            embed=embed,
            view=EdadView()
        )

    # ========================================================
    # ERROR
    # ========================================================

    @edad.error
    async def edad_error(self, ctx, error):

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ Necesitás permisos de administrador para usar este comando.",
                delete_after=5
            )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Edad(bot))