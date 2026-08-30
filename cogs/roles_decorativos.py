import os
import json
import re
import aiohttp
import aiofiles
import discord
from discord.ext import commands

# ============================================================
# CONFIGURACIÓN Y CONSTANTES
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "roles_decorativos.json")
MAX_ROLES_POR_USUARIO = 3
MAX_NOMBRE = 50
MAX_IMAGE_SIZE_BYTES = 2 * 1024 * 1024


# ============================================================
# FUNCIONES AUXILIARES ASINCRÓNICAS
# ============================================================

async def cargar_roles_async() -> dict:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        async with aiofiles.open(DATA_FILE, "r", encoding="utf-8") as f:
            contenido = await f.read()
            return json.loads(contenido) if contenido else {}
    except (json.JSONDecodeError, OSError):
        return {}


async def guardar_roles_async(data: dict) -> None:
    os.makedirs(DATA_FOLDER, exist_ok=True)
    async with aiofiles.open(DATA_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, indent=4, ensure_ascii=False))


def convertir_color(valor: str) -> discord.Color | None:
    valor = valor.strip().replace("#", "")
    if not re.fullmatch(r"[0-9a-fA-F]{6}", valor):
        return None
    try:
        return discord.Color(int(valor, 16))
    except ValueError:
        return None


# ============================================================
# MODALES
# ============================================================

class CrearRolModal(discord.ui.Modal, title="🎨 Crear rol decorativo"):

    nombre = discord.ui.TextInput(
        label="Nombre del rol",
        placeholder="Ej: 💜・violet",
        max_length=MAX_NOMBRE,
        required=True
    )

    color = discord.ui.TextInput(
        label="Color HEX",
        placeholder="Ej: #9B59B6",
        max_length=7,
        required=True
    )

    icono_url = discord.ui.TextInput(
        label="URL del ícono (Opcional)",
        placeholder="Ej: https://ejemplo.com/icono.png",
        required=False
    )

    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message(
                "❌ Este sistema solo funciona dentro de un servidor.", ephemeral=True
            )

        user_id = str(interaction.user.id)
        guild_id = str(guild.id)

        guild_data = self.cog.roles_cache.get(guild_id, {})
        creados = guild_data.get(user_id, [])
        creados_validos = [rid for rid in creados if guild.get_role(int(rid))]

        if len(creados_validos) >= MAX_ROLES_POR_USUARIO:
            return await interaction.response.send_message(
                f"❌ Ya posees el máximo de **{MAX_ROLES_POR_USUARIO} roles decorativos**.",
                ephemeral=True
            )

        nombre_val = self.nombre.value.strip()
        color_val = convertir_color(self.color.value)

        if not nombre_val:
            return await interaction.response.send_message("❌ Nombre inválido.", ephemeral=True)

        if color_val is None:
            return await interaction.response.send_message(
                "❌ Color inválido. Usa formato HEX (ej: `#9B59B6`).", ephemeral=True
            )

        icon_bytes = None
        url = self.icono_url.value.strip()

        if url:
            try:
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url) as resp:
                        content_type = resp.headers.get("Content-Type", "")
                        content_length = int(resp.headers.get("Content-Length", 0))

                        if resp.status == 200 and "image" in content_type:
                            if content_length > MAX_IMAGE_SIZE_BYTES:
                                return await interaction.response.send_message(
                                    "❌ La imagen excede el tamaño máximo (2MB).", ephemeral=True
                                )
                            icon_bytes = await resp.read()
                        else:
                            return await interaction.response.send_message(
                                "❌ La URL proporcionada no apunta a una imagen válida.", ephemeral=True
                            )
            except Exception:
                return await interaction.response.send_message(
                    "❌ Error de conexión al obtener la imagen.", ephemeral=True
                )

        bot_member = guild.me
        if bot_member is None:
            return await interaction.response.send_message("❌ Error al obtener datos del servidor.", ephemeral=True)

        try:
            role = await guild.create_role(
                name=nombre_val,
                color=color_val,
                display_icon=icon_bytes,
                permissions=discord.Permissions.none(),
                reason=f"Rol decorativo creado por {interaction.user}"
            )
        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ Sin permisos de **Gestionar roles** o el servidor requiere Nivel 2 de Boost para íconos.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            return await interaction.response.send_message(
                f"❌ Rechazado por Discord: `{e}`", ephemeral=True
            )

        await self.cog.registrar_rol(guild.id, interaction.user.id, role.id)

        try:
            if bot_member.top_role.position > 1:
                posicion = max(1, bot_member.top_role.position - 1)
                await role.edit(position=posicion)
        except (discord.Forbidden, discord.HTTPException):
            pass

        embed = discord.Embed(
            title="🎨・Rol Creado",
            description=(
                f"**Rol:** {role.mention}\n"
                f"**Color:** `{self.color.value}`\n"
                f"**Ícono:** {'Asignado' if icon_bytes else 'Sin ícono'}"
            ),
            color=color_val
        )
        await interaction.response.send_message(
            embed=embed,
            view=RolCreadoView(self.cog, role.id),
            ephemeral=True
        )


class CambiarColorModal(discord.ui.Modal, title="🎨 Cambiar color"):

    color = discord.ui.TextInput(label="Nuevo color HEX", placeholder="#FF00FF", max_length=7, required=True)

    def __init__(self, cog, role_id: int):
        super().__init__()
        self.cog = cog
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ El rol ya no existe.", ephemeral=True)

        if not self.cog.usuario_es_dueno(interaction.guild.id, interaction.user.id, self.role_id):
            return await interaction.response.send_message("❌ No eres el propietario de este rol.", ephemeral=True)

        color_val = convertir_color(self.color.value)
        if color_val is None:
            return await interaction.response.send_message("❌ Formato HEX inválido.", ephemeral=True)

        try:
            await role.edit(color=color_val, reason=f"Editado por {interaction.user}")
            await interaction.response.send_message(f"🎨 Color actualizado a `{self.color.value}`.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Falta de permisos para editar el rol.", ephemeral=True)


class CambiarNombreModal(discord.ui.Modal, title="✏️ Cambiar nombre"):

    nombre = discord.ui.TextInput(label="Nuevo nombre", max_length=MAX_NOMBRE, required=True)

    def __init__(self, cog, role_id: int):
        super().__init__()
        self.cog = cog
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ El rol ya no existe.", ephemeral=True)

        if not self.cog.usuario_es_dueno(interaction.guild.id, interaction.user.id, self.role_id):
            return await interaction.response.send_message("❌ No eres el propietario de este rol.", ephemeral=True)

        try:
            await role.edit(name=self.nombre.value.strip(), reason=f"Editado por {interaction.user}")
            await interaction.response.send_message(
                f"✏️ Nombre cambiado a **{discord.utils.escape_markdown(self.nombre.value)}**.", ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message("❌ Falta de permisos para editar el rol.", ephemeral=True)


class CompartirModal(discord.ui.Modal, title="🔗 Compartir rol"):

    mensaje = discord.ui.TextInput(
        label="Mensaje",
        placeholder="Ej: ¿Quién quiere mi rol?",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False
    )

    def __init__(self, cog, role_id: int):
        super().__init__()
        self.cog = cog
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):
        role = interaction.guild.get_role(self.role_id)
        if not role:
            return await interaction.response.send_message("❌ El rol ya no existe.", ephemeral=True)

        if not self.cog.usuario_es_dueno(interaction.guild.id, interaction.user.id, self.role_id):
            return await interaction.response.send_message("❌ No eres el propietario de este rol.", ephemeral=True)

        msg_texto = self.mensaje.value.strip() or "¿Quién quiere mi rol? 💜"

        embed = discord.Embed(
            title=f"{role.name}",
            description=f"{msg_texto}\n\nCreado por {interaction.user.mention}",
            color=role.color
        )
        embed.set_footer(text="Rol decorativo • Sin permisos de moderación")

        await interaction.response.send_message(
            embed=embed,
            view=ObtenerRolView(self.cog, role.id)
        )


# ============================================================
# COMPONENTES DE INTERFAZ (VISTAS Y SELECCIÓN)
# ============================================================

class SelectorRoles(discord.ui.Select):

    def __init__(self, cog, roles):
        options = [
            discord.SelectOption(
                label=role.name,
                value=str(role.id),
                emoji="🏷️"
            ) for role in roles
        ]
        super().__init__(
            placeholder="Selecciona uno de tus roles...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.cog = cog

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        role = interaction.guild.get_role(role_id)

        if not role:
            return await interaction.response.send_message("❌ Ese rol ya no existe.", ephemeral=True)

        embed = discord.Embed(
            title=f"Gestionar: {role.name}",
            description=f"Rol: {role.mention}\nID: `{role.id}`",
            color=role.color
        )
        await interaction.response.send_message(
            embed=embed,
            view=RolCreadoView(self.cog, role_id),
            ephemeral=True
        )


class MisRolesView(discord.ui.View):

    def __init__(self, cog, roles):
        super().__init__(timeout=180)
        self.add_item(SelectorRoles(cog, roles))


class ObtenerRolButton(discord.ui.Button):

    def __init__(self, cog, role_id: int):
        super().__init__(
            label="Obtener rol",
            emoji="🎨",
            style=discord.ButtonStyle.primary,
            custom_id=f"decorativo_obtener_{role_id}"
        )
        self.cog = cog
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        role = guild.get_role(self.role_id)

        if not role:
            return await interaction.response.send_message("❌ Este rol ya no existe.", ephemeral=True)

        if role in interaction.user.roles:
            return await interaction.response.send_message("💜 Ya posees este rol.", ephemeral=True)

        if guild.me.top_role <= role:
            return await interaction.response.send_message(
                "❌ Jerarquía insuficiente: El rol está por encima de mi nivel.", ephemeral=True
            )

        try:
            await interaction.user.add_roles(role, reason="Rol decorativo obtenido")
            await interaction.response.send_message(f"🎨 Asignado: {role.mention}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ No tengo permiso para asignar este rol.", ephemeral=True)


class ObtenerRolView(discord.ui.View):

    def __init__(self, cog, role_id: int):
        super().__init__(timeout=None)
        self.add_item(ObtenerRolButton(cog, role_id))


class RolCreadoView(discord.ui.View):

    def __init__(self, cog, role_id: int):
        super().__init__(timeout=300)
        self.cog = cog
        self.role_id = role_id

    @discord.ui.button(label="Compartir", emoji="🔗", style=discord.ButtonStyle.primary)
    async def compartir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cog.usuario_es_dueno(interaction.guild.id, interaction.user.id, self.role_id):
            return await interaction.response.send_message("❌ Este rol no te pertenece.", ephemeral=True)
        await interaction.response.send_modal(CompartirModal(self.cog, self.role_id))

    @discord.ui.button(label="Color", emoji="🎨", style=discord.ButtonStyle.secondary)
    async def cambiar_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cog.usuario_es_dueno(interaction.guild.id, interaction.user.id, self.role_id):
            return await interaction.response.send_message("❌ Este rol no te pertenece.", ephemeral=True)
        await interaction.response.send_modal(CambiarColorModal(self.cog, self.role_id))

    @discord.ui.button(label="Nombre", emoji="✏️", style=discord.ButtonStyle.secondary)
    async def cambiar_nombre(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cog.usuario_es_dueno(interaction.guild.id, interaction.user.id, self.role_id):
            return await interaction.response.send_message("❌ Este rol no te pertenece.", ephemeral=True)
        await interaction.response.send_modal(CambiarNombreModal(self.cog, self.role_id))

    @discord.ui.button(label="Eliminar", emoji="🗑️", style=discord.ButtonStyle.danger)
    async def eliminar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.cog.usuario_es_dueno(interaction.guild.id, interaction.user.id, self.role_id):
            return await interaction.response.send_message("❌ Este rol no te pertenece.", ephemeral=True)

        role = interaction.guild.get_role(self.role_id)
        if role:
            try:
                await role.delete(reason=f"Eliminado por {interaction.user}")
            except discord.Forbidden:
                return await interaction.response.send_message("❌ Error de permisos al eliminar.", ephemeral=True)

        await self.cog.eliminar_rol(interaction.guild.id, interaction.user.id, self.role_id)
        await interaction.response.send_message("🗑️ Rol eliminado correctamente.", ephemeral=True)


class RolesDecorativosView(discord.ui.View):

    def __init__(self, cog):
        super().__init__(timeout=None)
        self.cog = cog

    @discord.ui.button(label="Crear rol", emoji="🎨", style=discord.ButtonStyle.primary, custom_id="decorativos_crear")
    async def crear(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CrearRolModal(self.cog))


# ============================================================
# COG PRINCIPAL
# ============================================================

class RolesDecorativos(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.roles_cache = {}

    async def cog_load(self):
        self.roles_cache = await cargar_roles_async()
        self.bot.add_view(RolesDecorativosView(self))

    def usuario_es_dueno(self, guild_id: int, user_id: int, role_id: int) -> bool:
        guild_data = self.roles_cache.get(str(guild_id), {})
        user_roles = guild_data.get(str(user_id), [])
        return str(role_id) in [str(r) for r in user_roles]

    async def registrar_rol(self, guild_id: int, user_id: int, role_id: int):
        g_id, u_id, r_id = str(guild_id), str(user_id), str(role_id)
        if g_id not in self.roles_cache:
            self.roles_cache[g_id] = {}
        if u_id not in self.roles_cache[g_id]:
            self.roles_cache[g_id][u_id] = []
        
        self.roles_cache[g_id][u_id].append(r_id)
        await guardar_roles_async(self.roles_cache)

    async def eliminar_rol(self, guild_id: int, user_id: int, role_id: int):
        g_id, u_id, r_id = str(guild_id), str(user_id), str(role_id)
        if g_id in self.roles_cache and u_id in self.roles_cache[g_id]:
            self.roles_cache[g_id][u_id] = [x for x in self.roles_cache[g_id][u_id] if x != r_id]
            await guardar_roles_async(self.roles_cache)

    @commands.hybrid_command(name="rolesdecorativos", description="Abre el sistema de roles decorativos.")
    async def rolesdecorativos(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🎨・Roles Decorativos",
            description=(
                "Crea y administra tus roles personalizados.\n\n"
                f"Límite actual: **{MAX_ROLES_POR_USUARIO} roles** por usuario."
            ),
            color=discord.Color.from_rgb(155, 89, 182)
        )
        await ctx.send(embed=embed, view=RolesDecorativosView(self))

    @commands.hybrid_command(name="misroles", description="Muestra tus roles decorativos actuales.")
    async def misroles(self, ctx: commands.Context):
        guild_data = self.roles_cache.get(str(ctx.guild.id), {})
        roles_ids = guild_data.get(str(ctx.author.id), [])

        roles = [ctx.guild.get_role(int(rid)) for rid in roles_ids if ctx.guild.get_role(int(rid))]

        if not roles:
            return await ctx.send("🎨 No posees roles decorativos registrados.", ephemeral=True)

        embed = discord.Embed(
            title="🎨・Mis Roles Decorativos",
            description="Selecciona un rol del menú de abajo para administrarlo:",
            color=discord.Color.from_rgb(155, 89, 182)
        )
        await ctx.send(embed=embed, view=MisRolesView(self, roles), ephemeral=True)


async def setup(bot):
    await bot.add_cog(RolesDecorativos(bot))
