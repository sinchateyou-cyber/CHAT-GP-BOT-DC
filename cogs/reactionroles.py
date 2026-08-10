import json
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIG
# ============================================================

DATA_FILE = Path("data/roles.json")

DEFAULT_COLORS = {
    "🔴": "Rojo",
    "🟠": "Naranja",
    "🟡": "Amarillo",
    "🟢": "Verde",
    "🔵": "Azul",
    "🟣": "Violeta",
    "⚫": "Negro",
    "⚪": "Blanco",
}


# ============================================================
# DATA
# ============================================================

def load_roles():
    if not DATA_FILE.exists():
        return {"colores": {"titulo": "🎨 Colores",
                             "descripcion": "Elegí tu color favorito.",
                             "roles": DEFAULT_COLORS.copy()}}

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        data = {}

    data.setdefault("colores", {})
    data["colores"].setdefault("titulo", "🎨 Colores")
    data["colores"].setdefault("descripcion", "Elegí tu color favorito.")
    data["colores"].setdefault("roles", DEFAULT_COLORS.copy())

    return data


# ============================================================
# ROLE FINDER
# ============================================================

def find_role(guild: discord.Guild, configured_value: str):
    """
    Busca primero por ID y después por nombre.
    Esto permite usar roles.json con:
        "🟠": "Naranja"
    o:
        "🟠": "123456789012345678"
    """

    # Si el JSON tiene un ID
    try:
        role_id = int(configured_value)
    except (TypeError, ValueError):
        role_id = None

    if role_id:
        role = guild.get_role(role_id)
        if role:
            return role

    # Si el JSON tiene el nombre
    return discord.utils.find(
        lambda r: r.name.casefold() == str(configured_value).casefold(),
        guild.roles
    )


# ============================================================
# SELECT DE COLORES
# ============================================================

class ColorSelect(discord.ui.Select):
    def __init__(self):
        data = load_roles()
        roles = data["colores"]["roles"]

        options = []

        for emoji, role_name in roles.items():
            options.append(
                discord.SelectOption(
                    label=str(role_name)[:100],
                    value=str(emoji),
                    emoji=emoji,
                    description=f"Elegir {role_name}"[:100]
                )
            )

        super().__init__(
            placeholder="🎨 Elegí tu color...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="reactionroles:colores"
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild:
            return await interaction.response.send_message(
                "❌ Este menú solo funciona dentro de un servidor.",
                ephemeral=True
            )

        member = interaction.user
        if not isinstance(member, discord.Member):
            member = interaction.guild.get_member(interaction.user.id)

        if member is None:
            return await interaction.response.send_message(
                "❌ No pude encontrar tu usuario en el servidor.",
                ephemeral=True
            )

        emoji = self.values[0]

        data = load_roles()
        role_name = data["colores"]["roles"].get(emoji)

        if not role_name:
            return await interaction.response.send_message(
                "❌ Ese color no está configurado.",
                ephemeral=True
            )

        role = find_role(interaction.guild, role_name)

        # ====================================================
        # ESTE ES EL ARREGLO PRINCIPAL
        # ====================================================
        # roles.json guarda "Naranja", "Rojo", etc.
        # Ahora se busca el rol REAL del servidor por nombre.
        # ====================================================

        if role is None:
            return await interaction.response.send_message(
                f"❌ El rol **{role_name}** no existe en este servidor.\n"
                f"Creá un rol llamado exactamente **{role_name}** "
                f"o corregí `data/roles.json`.",
                ephemeral=True
            )

        # Discord no permite que el bot gestione roles que estén
        # por encima de su propio rol.
        me = interaction.guild.me

        if me is None or role >= me.top_role:
            return await interaction.response.send_message(
                f"❌ No puedo administrar el rol **{role.name}**.\n"
                "Subí el rol del bot por encima de los roles de colores.",
                ephemeral=True
            )

        # Quitar los demás colores
        color_role_names = set(data["colores"]["roles"].values())
        roles_to_remove = [
            r for r in member.roles
            if r.name in color_role_names and r != role
        ]

        try:
            if roles_to_remove:
                await member.remove_roles(
                    *roles_to_remove,
                    reason="Cambio de color mediante reaction roles"
                )

            # Si ya tenía el rol elegido, no lo duplicamos.
            if role in member.roles:
                await interaction.response.send_message(
                    f"🎨 Ya tenés seleccionado el color **{role.name}**.",
                    ephemeral=True
                )
                return

            await member.add_roles(
                role,
                reason="Selección de color mediante reaction roles"
            )

        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ Discord no me permite modificar ese rol. "
                "Revisá la posición del rol del bot y sus permisos.",
                ephemeral=True
            )

        except discord.HTTPException:
            return await interaction.response.send_message(
                "❌ Discord rechazó la modificación del rol. "
                "Probá nuevamente.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"✅ Listo, tu color ahora es **{role.name}**.",
            ephemeral=True
        )


class ColorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ColorSelect())


# ============================================================
# COG
# ============================================================

class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        # View persistente: el menú sigue funcionando después
        # de reiniciar el bot.
        self.bot.add_view(ColorView())

    @app_commands.command(
        name="roles",
        description="Configura los paneles de roles."
    )
    @app_commands.describe(tipo="Tipo de panel que querés enviar.")
    @app_commands.choices(
        tipo=[
            app_commands.Choice(name="🎨 Colores", value="colores")
        ]
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roles(self, interaction: discord.Interaction, tipo: app_commands.Choice[str]):
        if tipo.value != "colores":
            return await interaction.response.send_message(
                "❌ Tipo de panel no válido.",
                ephemeral=True
            )

        data = load_roles()
        config = data["colores"]

        embed = discord.Embed(
            title=config.get("titulo", "🎨 Colores"),
            description=(
                f"{config.get('descripcion', 'Elegí tu color favorito.')}\n\n"
                "👇 **Seleccioná una opción.**\n"
                "Podés cambiar tu selección cuando quieras."
            ),
            color=discord.Color.blurple()
        )

        embed.set_footer(text="Sistema de Reaction Roles")

        await interaction.response.send_message(
            embed=embed,
            view=ColorView()
        )

    @roles.error
    async def roles_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.MissingPermissions):
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ Necesitás el permiso **Gestionar roles**.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Necesitás el permiso **Gestionar roles**.",
                    ephemeral=True
                )
            return

        if interaction.response.is_done():
            await interaction.followup.send(
                f"❌ Ocurrió un error: `{error}`",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Ocurrió un error: `{error}`",
                ephemeral=True
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))