import discord
from discord.ext import commands
from discord import app_commands
import json
import os

ROLES_FILE = "data/roles.json"


# ============================================================
# CARGAR / GUARDAR ROLES
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
# SELECT DE ROLES
# ============================================================

class RoleSelect(discord.ui.Select):

    def __init__(self, categoria, titulo, opciones):
        self.categoria = categoria

        select_options = []

        for emoji, nombre in opciones.items():
            select_options.append(
                discord.SelectOption(
                    label=nombre,
                    emoji=emoji,
                    value=nombre
                )
            )

        super().__init__(
            placeholder=f"Seleccioná tu {titulo.lower()}...",
            min_values=0,
            max_values=1,
            options=select_options
        )

    async def callback(self, interaction: discord.Interaction):

        data = cargar_roles()

        guild_data = data.get(str(interaction.guild.id), {})
        categoria_data = guild_data.get("categorias", {}).get(self.categoria, {})

        roles = categoria_data.get("roles", {})

        # Quitar roles de esta categoría
        for role_name in roles.values():
            role = discord.utils.get(
                interaction.guild.roles,
                name=role_name
            )

            if role and role in interaction.user.roles:
                try:
                    await interaction.user.remove_roles(role)
                except discord.Forbidden:
                    pass

        # Si no eligió nada
        if not self.values:
            await interaction.response.send_message(
                "🗑️ **Rol eliminado correctamente.**",
                ephemeral=True
            )
            return

        role_name = self.values[0]

        role = discord.utils.get(
            interaction.guild.roles,
            name=role_name
        )

        if role is None:
            await interaction.response.send_message(
                f"❌ No encontré el rol **{role_name}**.",
                ephemeral=True
            )
            return

        try:
            await interaction.user.add_roles(role)

            await interaction.response.send_message(
                f"✅ **Rol asignado:** {role.mention}",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para asignarte ese rol.",
                ephemeral=True
            )


class RoleView(discord.ui.View):

    def __init__(self, categoria, titulo, opciones):
        super().__init__(timeout=None)

        self.add_item(
            RoleSelect(
                categoria,
                titulo,
                opciones
            )
        )


# ============================================================
# COG
# ============================================================

class ReactionRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # /ROLES
    # ========================================================

    @app_commands.command(
        name="roles",
        description="Muestra el panel para elegir tus roles."
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roles(self, interaction: discord.Interaction):

        data = cargar_roles()

        guild_id = str(interaction.guild.id)

        if guild_id not in data:
            await interaction.response.send_message(
                "❌ Este servidor todavía no tiene roles configurados.",
                ephemeral=True
            )
            return

        categorias = data[guild_id].get("categorias", {})

        embed = discord.Embed(
            title="✦ 𝐑𝐎𝐋𝐄𝐒 𝐃𝐄𝐋 𝐒𝐄𝐑𝐕𝐈𝐃𝐎𝐑 ✦",
            description=(
                "**Elegí tus roles utilizando los menús de abajo.**\n"
                "Podés cambiarlos cuando quieras.\n\n"
                "🟣 **Tus roles se asignan automáticamente.**"
            ),
            color=discord.Color.from_rgb(145, 70, 255)
        )

        embed.set_footer(
            text=f"{interaction.guild.name} • Sistema de roles"
        )

        await interaction.response.send_message(
            embed=embed
        )

        mensaje = await interaction.original_response()

        # Crear los menús debajo del embed
        for categoria, config in categorias.items():

            titulo = config.get("titulo", categoria)
            descripcion = config.get("descripcion", "")
            opciones = config.get("roles", {})

            if not opciones:
                continue

            await interaction.channel.send(
                f"**{titulo}**\n{descripcion}",
                view=RoleView(
                    categoria,
                    titulo,
                    opciones
                )
            )

    # ========================================================
    # /CREAR_ROLES
    # ========================================================

    @app_commands.command(
        name="crear_roles",
        description="Crea automáticamente los roles configurados."
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def crear_roles(self, interaction: discord.Interaction):

        data = cargar_roles()

        guild_id = str(interaction.guild.id)

        if guild_id not in data:
            await interaction.response.send_message(
                "❌ No hay configuración para este servidor.",
                ephemeral=True
            )
            return

        categorias = data[guild_id].get("categorias", {})

        creados = 0

        for config in categorias.values():

            roles = config.get("roles", {})

            for role_name in roles.values():

                existente = discord.utils.get(
                    interaction.guild.roles,
                    name=role_name
                )

                if existente:
                    continue

                try:
                    await interaction.guild.create_role(
                        name=role_name,
                        reason="Sistema de roles automáticos"
                    )

                    creados += 1

                except discord.Forbidden:
                    await interaction.response.send_message(
                        "❌ No tengo permisos para crear roles.",
                        ephemeral=True
                    )
                    return

        await interaction.response.send_message(
            f"✅ **Roles creados:** `{creados}`",
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))