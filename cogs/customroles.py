import json
import re
from pathlib import Path
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
    "😀 **Icono:** elegí un emoji personalizado del servidor\n\n"
    "No necesitás permisos de moderador."
)
MAX_ROLE_NAME_LENGTH = 100
MAX_EMOJIS_PER_PAGE = 25
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
            DATA_FILE.read_text(
                encoding="utf-8"
            )
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
    color_text = color_text.strip()
    if color_text.startswith("#"):
        color_text = color_text[1:]
    if color_text.lower().startswith("0x"):
        color_text = color_text[2:]
    if not re.fullmatch(
        r"[0-9a-fA-F]{6}",
        color_text
    ):
        return None
    return discord.Color(
        int(color_text, 16)
    )
# ============================================================
# MODAL CREAR ROL
# ============================================================
class CreateRoleModal(
    discord.ui.Modal,
    title="🎨 Crear tu rol"
):
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
    def __init__(
        self,
        selected_emoji: discord.Emoji
    ):
        super().__init__()
        self.selected_emoji = selected_emoji
    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        cog = interaction.client.get_cog(
            "CustomRoles"
        )
        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema de roles no está disponible.",
                ephemeral=True
            )
        await cog.create_custom_role(
            interaction,
            str(self.nombre.value),
            str(self.color.value),
            self.selected_emoji
        )
# ============================================================
# MODAL EDITAR ROL
# ============================================================
class EditRoleModal(
    discord.ui.Modal,
    title="✏️ Editar tu rol"
):
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
    def __init__(
        self,
        selected_emoji: discord.Emoji
    ):
        super().__init__()
        self.selected_emoji = selected_emoji
    async def on_submit(
        self,
        interaction: discord.Interaction
    ):
        cog = interaction.client.get_cog(
            "CustomRoles"
        )
        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema de roles no está disponible.",
                ephemeral=True
            )
        await cog.edit_custom_role(
            interaction,
            str(self.nombre.value),
            str(self.color.value),
            self.selected_emoji
        )
# ============================================================
# SELECTOR DE EMOJIS
# ============================================================
class EmojiSelect(
    discord.ui.Select
):
    def __init__(
        self,
        emojis,
        page=0
    ):
        self.page = page
        self.emojis = emojis
        start = page * MAX_EMOJIS_PER_PAGE
        end = start + MAX_EMOJIS_PER_PAGE
        page_emojis = emojis[
            start:end
        ]
        options = []
        for emoji in page_emojis:
            options.append(
                discord.SelectOption(
                    label=emoji.name[:100],
                    value=str(emoji.id),
                    emoji=emoji,
                    description=(
                        "Elegir este emoji "
                        "como icono del rol"
                    )
                )
            )
        super().__init__(
            placeholder="😀 Elegí un emoji del servidor...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"customroles:emoji:{page}"
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        emoji_id = int(
            self.values[0]
        )
        emoji = interaction.guild.get_emoji(
            emoji_id
        )
        if emoji is None:
            return await interaction.response.send_message(
                "❌ Ese emoji ya no existe en el servidor.",
                ephemeral=True
            )
        await interaction.response.send_modal(
            CreateRoleModal(emoji)
        )
# ============================================================
# BOTONES DE PAGINACIÓN
# ============================================================
class EmojiPaginationView(
    discord.ui.View
):
    def __init__(
        self,
        emojis,
        page=0
    ):
        super().__init__(
            timeout=180
        )
        self.emojis = emojis
        self.page = page
        self.max_page = max(
            0,
            (len(emojis) - 1) //
            MAX_EMOJIS_PER_PAGE
        )
        # Selector
        self.add_item(
            EmojiSelect(
                emojis,
                page
            )
        )
        # Botón anterior
        previous_button = discord.ui.Button(
            label="◀️",
            style=discord.ButtonStyle.secondary,
            disabled=page <= 0
        )
        previous_button.callback = (
            self.previous_page
        )
        self.add_item(
            previous_button
        )
        # Botón siguiente
        next_button = discord.ui.Button(
            label="▶️",
            style=discord.ButtonStyle.secondary,
            disabled=page >= self.max_page
        )
        next_button.callback = (
            self.next_page
        )
        self.add_item(
            next_button
        )
    async def previous_page(
        self,
        interaction: discord.Interaction
    ):
        new_page = self.page - 1
        if new_page < 0:
            new_page = 0
        await self.change_page(
            interaction,
            new_page
        )
    async def next_page(
        self,
        interaction: discord.Interaction
    ):
        new_page = self.page + 1
        if new_page > self.max_page:
            new_page = self.max_page
        await self.change_page(
            interaction,
            new_page
        )
    async def change_page(
        self,
        interaction: discord.Interaction,
        page: int
    ):
        new_view = EmojiPaginationView(
            self.emojis,
            page
        )
        total_pages = self.max_page + 1
        embed = discord.Embed(
            title="😀 Elegí el icono de tu rol",
            description=(
                "Seleccioná uno de los emojis "
                "personalizados del servidor.\n\n"
                f"📄 **Página:** {page + 1}/{total_pages}"
            ),
            color=discord.Color.from_rgb(
                138,
                43,
                226
            )
        )
        await interaction.response.edit_message(
            embed=embed,
            view=new_view
        )
# ============================================================
# VISTA PRINCIPAL
# ============================================================
class CustomRoleView(
    discord.ui.View
):
    def __init__(self):
        super().__init__(
            timeout=None
        )
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
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message(
                "❌ Esto solo funciona dentro de un servidor.",
                ephemeral=True
            )
        # Obtener solamente emojis personalizados
        emojis = list(
            guild.emojis
        )
        if not emojis:
            return await interaction.response.send_message(
                "❌ Este servidor no tiene emojis personalizados.\n\n"
                "Agregá al menos un emoji al servidor "
                "para poder usarlo como icono.",
                ephemeral=True
            )
        # Ordenar por nombre
        emojis.sort(
            key=lambda e: e.name.lower()
        )
        embed = discord.Embed(
            title="😀 Elegí el icono de tu rol",
            description=(
                "Seleccioná un emoji personalizado "
                "del servidor.\n\n"
                "Después vas a poder elegir el "
                "nombre y el color de tu rol."
            ),
            color=discord.Color.from_rgb(
                138,
                43,
                226
            )
        )
        total_pages = (
            (len(emojis) - 1) //
            MAX_EMOJIS_PER_PAGE
        ) + 1
        embed.set_footer(
            text=f"Página 1/{total_pages}"
        )
        await interaction.response.send_message(
            embed=embed,
            view=EmojiPaginationView(
                emojis,
                0
            ),
            ephemeral=True
        )
# ============================================================
# VISTA DE GESTIÓN
# ============================================================
class ManageRoleView(
    discord.ui.View
):
    def __init__(self):
        super().__init__(
            timeout=None
        )
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
        cog = interaction.client.get_cog(
            "CustomRoles"
        )
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
        # Obtener emojis
        emojis = list(
            interaction.guild.emojis
        )
        if not emojis:
            return await interaction.response.send_message(
                "❌ Este servidor no tiene emojis personalizados.",
                ephemeral=True
            )
        emojis.sort(
            key=lambda e: e.name.lower()
        )
        embed = discord.Embed(
            title="✏️ Editar tu rol",
            description=(
                "Primero elegí el nuevo emoji "
                "que querés utilizar como icono."
            ),
            color=discord.Color.from_rgb(
                138,
                43,
                226
            )
        )
        total_pages = (
            (len(emojis) - 1) //
            MAX_EMOJIS_PER_PAGE
        ) + 1
        embed.set_footer(
            text=f"Página 1/{total_pages}"
        )
        await interaction.response.send_message(
            embed=embed,
            view=EditEmojiPaginationView(
                emojis,
                0
            ),
            ephemeral=True
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
        cog = interaction.client.get_cog(
            "CustomRoles"
        )
        if cog is None:
            return await interaction.response.send_message(
                "❌ El sistema no está disponible.",
                ephemeral=True
            )
        await cog.delete_custom_role(
            interaction
        )
# ============================================================
# SELECTOR DE EMOJIS PARA EDITAR
# ============================================================
class EditEmojiSelect(
    discord.ui.Select
):
    def __init__(
        self,
        emojis,
        page=0
    ):
        self.page = page
        start = page * MAX_EMOJIS_PER_PAGE
        end = start + MAX_EMOJIS_PER_PAGE
        page_emojis = emojis[
            start:end
        ]
        options = []
        for emoji in page_emojis:
            options.append(
                discord.SelectOption(
                    label=emoji.name[:100],
                    value=str(emoji.id),
                    emoji=emoji,
                    description="Usar este emoji como icono"
                )
            )
        super().__init__(
            placeholder="😀 Elegí el nuevo emoji...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id=f"customroles:edit_emoji:{page}"
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        emoji_id = int(
            self.values[0]
        )
        emoji = interaction.guild.get_emoji(
            emoji_id
        )
        if emoji is None:
            return await interaction.response.send_message(
                "❌ Ese emoji ya no existe.",
                ephemeral=True
            )
        await interaction.response.send_modal(
            EditRoleModal(emoji)
        )
# ============================================================
# PAGINACIÓN EDITAR
# ============================================================
class EditEmojiPaginationView(
    discord.ui.View
):
    def __init__(
        self,
        emojis,
        page=0
    ):
        super().__init__(
            timeout=180
        )
        self.emojis = emojis
        self.page = page
        self.max_page = max(
            0,
            (len(emojis) - 1) //
            MAX_EMOJIS_PER_PAGE
        )
        self.add_item(
            EditEmojiSelect(
                emojis,
                page
            )
        )
        previous_button = discord.ui.Button(
            label="◀️",
            style=discord.ButtonStyle.secondary,
            disabled=page <= 0
        )
        previous_button.callback = (
            self.previous_page
        )
        self.add_item(
            previous_button
        )
        next_button = discord.ui.Button(
            label="▶️",
            style=discord.ButtonStyle.secondary,
            disabled=page >= self.max_page
        )
        next_button.callback = (
            self.next_page
        )
        self.add_item(
            next_button
        )
    async def previous_page(
        self,
        interaction
    ):
        await self.change_page(
            interaction,
            max(0, self.page - 1)
        )
    async def next_page(
        self,
        interaction
    ):
        await self.change_page(
            interaction,
            min(
                self.max_page,
                self.page + 1
            )
        )
    async def change_page(
        self,
        interaction,
        page
    ):
        view = EditEmojiPaginationView(
            self.emojis,
            page
        )
        total_pages = self.max_page + 1
        embed = discord.Embed(
            title="✏️ Editar tu rol",
            description=(
                "Elegí el nuevo emoji "
                "para tu rol."
            ),
            color=discord.Color.from_rgb(
                138,
                43,
                226
            )
        )
        embed.set_footer(
            text=f"Página {page + 1}/{total_pages}"
        )
        await interaction.response.edit_message(
            embed=embed,
            view=view
        )
# ============================================================
# COG
# ============================================================
class CustomRoles(
    commands.Cog
):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
        self.data = load_data()
    # ========================================================
    # COG LOAD
    # ========================================================
    async def cog_load(self):
        self.bot.add_view(
            CustomRoleView()
        )
        self.bot.add_view(
            ManageRoleView()
        )
        print(
            "✅ CustomRoles cargado."
        )
    # ========================================================
    # OBTENER ROL
    # ========================================================
    def get_user_role(
        self,
        guild_id,
        user_id
    ):
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
    # CREAR ROL
    # ========================================================
    async def create_custom_role(
        self,
        interaction,
        name,
        color_text,
        emoji
    ):
        guild = interaction.guild
        user = interaction.user
        if guild is None:
            return await interaction.response.send_message(
                "❌ Esto solo funciona dentro de un servidor.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # COMPROBAR ROL EXISTENTE
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
                    f"❌ Ya tenés un rol personalizado: "
                    f"{existing_role.mention}",
                    ephemeral=True
                )
            self.data.setdefault(
                str(guild.id),
                {}
            ).setdefault(
                "users",
                {}
            ).pop(
                str(user.id),
                None
            )
            save_data(
                self.data
            )
        # ----------------------------------------------------
        # COLOR
        # ----------------------------------------------------
        role_color = parse_color(
            color_text
        )
        if role_color is None:
            return await interaction.response.send_message(
                "❌ El color no es válido.\n\n"
                "Usá un formato como:\n"
                "`#8A2BE2`",
                ephemeral=True
            )
        # ----------------------------------------------------
        # COMPROBAR EMOJI
        # ----------------------------------------------------
        server_emoji = guild.get_emoji(
            emoji.id
        )
        if server_emoji is None:
            return await interaction.response.send_message(
                "❌ Ese emoji ya no pertenece al servidor.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # PERMISOS
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
                name=name.strip()[
                    :MAX_ROLE_NAME_LENGTH
                ],
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
                "❌ Discord rechazó la creación del rol.\n"
                f"`{e}`",
                ephemeral=True
            )
        # ----------------------------------------------------
        # ICONO
        # ----------------------------------------------------
        icon_error = None
        try:
            await role.edit(
                display_icon=server_emoji,
                reason=f"Icono del rol de {user}"
            )
        except discord.Forbidden:
            icon_error = (
                "No tengo permiso para colocar "
                "el icono del rol."
            )
        except discord.HTTPException as e:
            icon_error = (
                f"Discord rechazó el icono: `{e}`"
            )
        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------
        guild_id = str(
            guild.id
        )
        user_id = str(
            user.id
        )
        self.data.setdefault(
            guild_id,
            {}
        ).setdefault(
            "users",
            {}
        )
        self.data[guild_id][
            "users"
        ][user_id] = role.id
        save_data(
            self.data
        )
        # ----------------------------------------------------
        # ASIGNAR
        # ----------------------------------------------------
        try:
            await user.add_roles(
                role,
                reason="Rol personalizado"
            )
        except discord.Forbidden:
            try:
                await role.delete(
                    reason="No se pudo asignar el rol"
                )
            except Exception:
                pass
            self.data[guild_id][
                "users"
            ].pop(
                user_id,
                None
            )
            save_data(
                self.data
            )
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
                f"😀 **Icono:** {server_emoji}\n"
                f"👤 **Dueño:** {user.mention}"
            ),
            color=role_color
        )
        if icon_error:
            embed.add_field(
                name="⚠️ Icono",
                value=icon_error,
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
        emoji
    ):
        guild = interaction.guild
        user = interaction.user
        if guild is None:
            return await interaction.response.send_message(
                "❌ Esto solo funciona dentro de un servidor.",
                ephemeral=True
            )
        role_id = self.get_user_role(
            guild.id,
            user.id
        )
        if not role_id:
            return await interaction.response.send_message(
                "❌ No tenés un rol personalizado.",
                ephemeral=True
            )
        role = guild.get_role(
            role_id
        )
        if role is None:
            self.data.setdefault(
                str(guild.id),
                {}
            ).setdefault(
                "users",
                {}
            ).pop(
                str(user.id),
                None
            )
            save_data(
                self.data
            )
            return await interaction.response.send_message(
                "❌ Tu rol ya no existe.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # COLOR
        # ----------------------------------------------------
        color = parse_color(
            color_text
        )
        if color is None:
            return await interaction.response.send_message(
                "❌ El color no es válido.\n"
                "Ejemplo: `#8A2BE2`",
                ephemeral=True
            )
        # ----------------------------------------------------
        # EMOJI
        # ----------------------------------------------------
        server_emoji = guild.get_emoji(
            emoji.id
        )
        if server_emoji is None:
            return await interaction.response.send_message(
                "❌ Ese emoji ya no pertenece al servidor.",
                ephemeral=True
            )
        # ----------------------------------------------------
        # EDITAR
        # ----------------------------------------------------
        try:
            await role.edit(
                name=name.strip()[
                    :MAX_ROLE_NAME_LENGTH
                ],
                color=color,
                display_icon=server_emoji,
                reason=f"Rol editado por {user}"
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No puedo editar este rol.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            return await interaction.response.send_message(
                "❌ Discord rechazó la modificación.\n"
                f"`{e}`",
                ephemeral=True
            )
        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------
        embed = discord.Embed(
            title="✏️ Rol actualizado",
            description=(
                f"Tu rol {role.mention} fue actualizado.\n\n"
                f"🎨 **Color:** `{color_text}`\n"
                f"😀 **Icono:** {server_emoji}"
            ),
            color=color
        )
        await interaction.response.send_message(
            embed=embed,
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
        if guild is None:
            return await interaction.response.send_message(
                "❌ Esto solo funciona dentro de un servidor.",
                ephemeral=True
            )
        role_id = self.get_user_role(
            guild.id,
            user.id
        )
        if not role_id:
            return await interaction.response.send_message(
                "❌ No tenés un rol personalizado.",
                ephemeral=True
            )
        role = guild.get_role(
            role_id
        )
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
        save_data(
            self.data
        )
        if role:
            try:
                await role.delete(
                    reason=f"Rol eliminado por {user}"
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
    # PANEL
    # ========================================================
    @app_commands.command(
        name="crearrolpanel",
        description=(
            "Crea el panel para que los usuarios "
            "puedan crear sus propios roles."
        )
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
                "Tocá **Crear mi rol**.\n\n"
                "1️⃣ Elegí un emoji del servidor.\n"
                "2️⃣ Escribí el nombre del rol.\n"
                "3️⃣ Elegí el color.\n"
                "4️⃣ El bot lo crea y te lo asigna automáticamente."
            ),
            inline=False
        )
        embed.set_footer(
            text=(
                f"{interaction.guild.name} • "
                "Roles personalizados"
            )
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