import os
import json
import re
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "customroles.json"

PANEL_TITLE = "🎨 Crea tu propio rol"
PANEL_DESCRIPTION = (
    "Personalizá tu perfil creando tu propio rol.\n\n"
    "📝 **Nombre:** elegí cómo se llamará\n"
    "🎨 **Color:** elegí el color que quieras\n"
    "🖼️ **Icono:** agregá un icono al rol\n\n"
    "No necesitás permisos de moderador."
)

MAX_ROLE_NAME_LENGTH = 100

# Límite para evitar que un usuario cree infinitos roles.
MAX_ROLES_PER_USER = 1


# ============================================================
# DATOS
# ============================================================

def ensure_data():
    DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text(
            "{}",
            encoding="utf-8"
        )


def load_data():
    ensure_data()

    try:
        return json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )
    except Exception:
        return {}


def save_data(data):
    ensure_data()

    DATA_FILE.write_text(
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


# ============================================================
# UTILIDADES
# ============================================================

def parse_color(color_text: str):
    """
    Acepta:
    #8A2BE2
    8A2BE2
    0x8A2BE2
    """

    color_text = color_text.strip().replace("#", "")

    if color_text.lower().startswith("0x"):
        color_text = color_text[2:]

    if not re.fullmatch(r"[0-9a-fA-F]{6}", color_text):
        return None

    return discord.Color(int(color_text, 16))


async def download_image(url: str):
    """
    Descarga una imagen desde una URL.
    """

    if not url:
        return None

    if not url.startswith(("http://", "https://")):
        return None

    try:
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(
            timeout=timeout
        ) as session:

            async with session.get(url) as response:

                if response.status != 200:
                    return None

                content_type = response.headers.get(
                    "Content-Type",
                    ""
                ).lower()

                if not content_type.startswith("image/"):
                    return None

                data = await response.read()

                # Evitar imágenes gigantes.
                if len(data) > 256 * 1024:
                    return None

                return data

    except Exception:
        return None


# ============================================================
# MODAL CREAR ROL
# ============================================================

class CreateRoleModal(discord.ui.Modal, title="🎨 Crear tu rol"):

    nombre = discord.ui.TextInput(
        label="Nombre del rol",
        placeholder="Ej: Valentin",
        max_length=100,
        required=True
    )

    color = discord.ui.TextInput(
        label="Color HEX",
        placeholder="Ej: #8A2BE2",
        max_length=7,
        required=True
    )

    icono = discord.ui.TextInput(
        label="URL del icono (opcional)",
        placeholder="https://ejemplo.com/icono.png",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):

        cog = interaction.client.get_cog("CustomRoles")

        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema de roles no está disponible.",
                ephemeral=True
            )

        await cog.create_custom_role(
            interaction,
            str(self.nombre.value),
            str(self.color.value),
            str(self.icono.value).strip()
        )


# ============================================================
# MODAL EDITAR ROL
# ============================================================

class EditRoleModal(discord.ui.Modal, title="✏️ Editar tu rol"):

    nombre = discord.ui.TextInput(
        label="Nuevo nombre",
        placeholder="Ej: Valentin",
        max_length=100,
        required=True
    )

    color = discord.ui.TextInput(
        label="Nuevo color HEX",
        placeholder="Ej: #8A2BE2",
        max_length=7,
        required=True
    )

    icono = discord.ui.TextInput(
        label="Nueva URL del icono",
        placeholder="https://ejemplo.com/icono.png",
        required=False,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):

        cog = interaction.client.get_cog("CustomRoles")

        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema de roles no está disponible.",
                ephemeral=True
            )

        await cog.edit_custom_role(
            interaction,
            str(self.nombre.value),
            str(self.color.value),
            str(self.icono.value).strip()
        )


# ============================================================
# MODAL SOLO NOMBRE
# ============================================================

class RenameRoleModal(discord.ui.Modal, title="📝 Cambiar nombre"):

    nombre = discord.ui.TextInput(
        label="Nuevo nombre",
        placeholder="Ej: Valentin",
        max_length=100,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):

        cog = interaction.client.get_cog("CustomRoles")

        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema no está disponible.",
                ephemeral=True
            )

        await cog.rename_role(
            interaction,
            str(self.nombre.value)
        )


# ============================================================
# VISTA PRINCIPAL
# ============================================================

class CustomRoleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Crear mi rol",
        emoji="✨",
        style=discord.ButtonStyle.primary,
        custom_id="customroles:create"
    )
    async def create_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            CreateRoleModal()
        )


# ============================================================
# VISTA DE GESTIÓN
# ============================================================

class ManageRoleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Editar",
        emoji="✏️",
        style=discord.ButtonStyle.primary,
        custom_id="customroles:edit"
    )
    async def edit_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        cog = interaction.client.get_cog("CustomRoles")

        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema no está disponible.",
                ephemeral=True
            )

        if not cog.get_user_role(
            interaction.guild.id,
            interaction.user.id
        ):
            return await interaction.response.send_message(
                "❌ No tenés un rol personalizado.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            EditRoleModal()
        )

    @discord.ui.button(
        label="Eliminar",
        emoji="🗑️",
        style=discord.ButtonStyle.danger,
        custom_id="customroles:delete"
    )
    async def delete_role(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        cog = interaction.client.get_cog("CustomRoles")

        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema no está disponible.",
                ephemeral=True
            )

        await cog.delete_custom_role(
            interaction
        )


# ============================================================
# COG
# ============================================================

class CustomRoles(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.data = load_data()

    # ========================================================
    # EVENTO COG LOAD
    # ========================================================

    async def cog_load(self):

        # Registrar botones persistentes.
        self.bot.add_view(CustomRoleView())
        self.bot.add_view(ManageRoleView())

        print("✅ CustomRoles cargado.")

    # ========================================================
    # OBTENER ROL DEL USUARIO
    # ========================================================

    def get_user_role(self, guild_id, user_id):

        guild_data = self.data.get(
            str(guild_id),
            {}
        )

        roles = guild_data.get(
            "users",
            {}
        )

        role_id = roles.get(
            str(user_id)
        )

        if not role_id:
            return None

        return int(role_id)

    # ========================================================
    # COMPROBAR SI YA TIENE ROL
    # ========================================================

    def user_has_role(self, guild_id, user_id):

        return self.get_user_role(
            guild_id,
            user_id
        ) is not None

    # ========================================================
    # CREAR ROL
    # ========================================================

    async def create_custom_role(
        self,
        interaction,
        name,
        color_text,
        icon_url
    ):

        guild = interaction.guild
        user = interaction.user

        if guild is None:
            return await interaction.response.send_message(
                "❌ Esto solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # COMPROBAR SI YA TIENE UNO
        # ----------------------------------------------------

        existing_role_id = self.get_user_role(
            guild.id,
            user.id
        )

        if existing_role_id:

            existing_role = guild.get_role(
                existing_role_id
            )

            if existing_role:

                return await interaction.response.send_message(
                    f"❌ Ya tenés un rol personalizado: {existing_role.mention}",
                    ephemeral=True
                )

        # ----------------------------------------------------
        # COLOR
        # ----------------------------------------------------

        role_color = parse_color(color_text)

        if role_color is None:

            return await interaction.response.send_message(
                "❌ El color no es válido.\n\n"
                "Usá un formato como:\n"
                "`#8A2BE2`",
                ephemeral=True
            )

        # ----------------------------------------------------
        # COMPROBAR PERMISOS DEL BOT
        # ----------------------------------------------------

        me = guild.me

        if me is None:

            return await interaction.response.send_message(
                "❌ No pude comprobar mis permisos.",
                ephemeral=True
            )

        if not me.guild_permissions.manage_roles:

            return await interaction.response.send_message(
                "❌ Necesito el permiso **Gestionar roles**.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # CREAR ROL
        # ----------------------------------------------------

        try:

            role = await guild.create_role(
                name=name[:MAX_ROLE_NAME_LENGTH],
                color=role_color,
                reason=f"Rol personalizado de {user}"
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No tengo permiso para crear roles.",
                ephemeral=True
            )

        except discord.HTTPException as e:

            return await interaction.response.send_message(
                f"❌ Discord rechazó la creación del rol.\n"
                f"`{e}`",
                ephemeral=True
            )

        # ----------------------------------------------------
        # ICONO
        # ----------------------------------------------------

        icon_error = None

        if icon_url:

            image_data = await download_image(
                icon_url
            )

            if image_data:

                try:

                    await role.edit(
                        display_icon=image_data,
                        reason=f"Icono del rol de {user}"
                    )

                except discord.HTTPException as e:

                    icon_error = str(e)

            else:

                icon_error = (
                    "No pude descargar el icono. "
                    "Revisá que la URL sea directa a una imagen."
                )

        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        guild_id = str(guild.id)
        user_id = str(user.id)

        if guild_id not in self.data:

            self.data[guild_id] = {
                "users": {}
            }

        if "users" not in self.data[guild_id]:

            self.data[guild_id]["users"] = {}

        self.data[guild_id]["users"][user_id] = role.id

        save_data(self.data)

        # ----------------------------------------------------
        # ASIGNAR ROL
        # ----------------------------------------------------

        try:

            await user.add_roles(
                role,
                reason="Rol personalizado"
            )

        except discord.Forbidden:

            # Si no pudo asignarlo, borrar el rol creado.
            try:
                await role.delete(
                    reason="No se pudo asignar el rol"
                )
            except Exception:
                pass

            del self.data[guild_id]["users"][user_id]
            save_data(self.data)

            return await interaction.response.send_message(
                "❌ Creé el rol, pero no pude asignártelo.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------

        embed = discord.Embed(
            title="✨ Rol creado",
            description=(
                f"Tu rol {role.mention} fue creado correctamente.\n\n"
                f"🎨 **Color:** `{color_text}`\n"
                f"👤 **Dueño:** {user.mention}"
            ),
            color=role_color
        )

        if icon_error:

            embed.add_field(
                name="🖼️ Icono",
                value=f"⚠️ {icon_error}",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # EDITAR ROL
    # ========================================================

    async def edit_custom_role(
        self,
        interaction,
        name,
        color_text,
        icon_url
    ):

        guild = interaction.guild
        user = interaction.user

        role_id = self.get_user_role(
            guild.id,
            user.id
        )

        if not role_id:

            return await interaction.response.send_message(
                "❌ No tenés un rol personalizado.",
                ephemeral=True
            )

        role = guild.get_role(role_id)

        if role is None:

            self.data[str(guild.id)]["users"].pop(
                str(user.id),
                None
            )

            save_data(self.data)

            return await interaction.response.send_message(
                "❌ Tu rol ya no existe.",
                ephemeral=True
            )

        color = parse_color(color_text)

        if color is None:

            return await interaction.response.send_message(
                "❌ El color no es válido.\n"
                "Ejemplo: `#8A2BE2`",
                ephemeral=True
            )

        # ----------------------------------------------------
        # EDITAR
        # ----------------------------------------------------

        try:

            await role.edit(
                name=name[:MAX_ROLE_NAME_LENGTH],
                color=color,
                reason=f"Rol personalizado editado por {user}"
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No puedo editar este rol.",
                ephemeral=True
            )

        except discord.HTTPException:

            return await interaction.response.send_message(
                "❌ Discord rechazó la modificación.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # ICONO
        # ----------------------------------------------------

        icon_error = None

        if icon_url:

            image_data = await download_image(
                icon_url
            )

            if image_data:

                try:

                    await role.edit(
                        display_icon=image_data,
                        reason=f"Icono editado por {user}"
                    )

                except discord.HTTPException as e:

                    icon_error = str(e)

            else:

                icon_error = (
                    "No pude descargar el icono."
                )

        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------

        embed = discord.Embed(
            title="✏️ Rol actualizado",
            description=(
                f"Tu rol {role.mention} fue actualizado.\n\n"
                f"🎨 **Color:** `{color_text}`"
            ),
            color=color
        )

        if icon_error:

            embed.add_field(
                name="🖼️ Icono",
                value=f"⚠️ {icon_error}",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # CAMBIAR NOMBRE
    # ========================================================

    async def rename_role(
        self,
        interaction,
        name
    ):

        guild = interaction.guild
        user = interaction.user

        role_id = self.get_user_role(
            guild.id,
            user.id
        )

        if not role_id:

            return await interaction.response.send_message(
                "❌ No tenés un rol personalizado.",
                ephemeral=True
            )

        role = guild.get_role(role_id)

        if role is None:

            return await interaction.response.send_message(
                "❌ Tu rol ya no existe.",
                ephemeral=True
            )

        try:

            await role.edit(
                name=name[:MAX_ROLE_NAME_LENGTH],
                reason=f"Nombre cambiado por {user}"
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No puedo modificar tu rol.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"✅ Cambié el nombre de tu rol a **{name}**.",
            ephemeral=True
        )

    # ========================================================
    # ELIMINAR ROL
    # ========================================================

    async def delete_custom_role(
        self,
        interaction
    ):

        guild = interaction.guild
        user = interaction.user

        role_id = self.get_user_role(
            guild.id,
            user.id
        )

        if not role_id:

            return await interaction.response.send_message(
                "❌ No tenés un rol personalizado.",
                ephemeral=True
            )

        role = guild.get_role(role_id)

        # Borrar del JSON primero.
        guild_data = self.data.get(
            str(guild.id),
            {}
        )

        users = guild_data.get(
            "users",
            {}
        )

        users.pop(
            str(user.id),
            None
        )

        save_data(self.data)

        if role:

            try:

                await role.delete(
                    reason=f"Rol personalizado eliminado por {user}"
                )

            except discord.Forbidden:

                return await interaction.response.send_message(
                    "⚠️ Quité el registro de tu rol, "
                    "pero no tengo permiso para eliminarlo.",
                    ephemeral=True
                )

            except discord.HTTPException:

                return await interaction.response.send_message(
                    "⚠️ No pude eliminar el rol.",
                    ephemeral=True
                )

        await interaction.response.send_message(
            "🗑️ **Tu rol personalizado fue eliminado.**",
            ephemeral=True
        )

    # ========================================================
    # COMANDO PANEL
    # ========================================================

    @app_commands.command(
        name="crearrolpanel",
        description="Crea el panel para que los usuarios puedan crear sus propios roles."
    )
    @app_commands.default_permissions(
        administrator=True
    )
    async def crearrolpanel(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            return await interaction.response.send_message(
                "❌ Este comando solo funciona en servidores.",
                ephemeral=True
            )

        embed = discord.Embed(
            title=PANEL_TITLE,
            description=PANEL_DESCRIPTION,
            color=discord.Color.from_rgb(
                138,
                43,
                226
            )
        )

        embed.add_field(
            name="✨ ¿Cómo funciona?",
            value=(
                "Tocá **Crear mi rol** y completá el formulario.\n\n"
                "El rol será creado y asignado automáticamente."
            ),
            inline=False
        )

        embed.set_footer(
            text=f"{interaction.guild.name} • Roles personalizados"
        )

        await interaction.channel.send(
            embed=embed,
            view=CustomRoleView()
        )

        await interaction.response.send_message(
            "✅ Panel de roles creado correctamente.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        CustomRoles(bot)
    )