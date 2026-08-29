import discord
from discord.ext import commands
import json
import os
import re
import aiohttp


# ============================================================
# CONFIGURACIÓN
# ============================================================

DATA_FOLDER = "data"
DATA_FILE = os.path.join(DATA_FOLDER, "roles_decorativos.json")

# Máximo de roles decorativos que puede crear cada usuario
MAX_ROLES_POR_USUARIO = 3

# Máximo de caracteres para el nombre
MAX_NOMBRE = 50


# ============================================================
# ARCHIVO JSON
# ============================================================

def cargar_roles():
    os.makedirs(DATA_FOLDER, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return {}


def guardar_roles(data):
    os.makedirs(DATA_FOLDER, exist_ok=True)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# COLOR HEX
# ============================================================

def convertir_color(valor):
    """
    Convierte:
    #9b59b6
    9b59b6
    """

    valor = valor.strip().replace("#", "")

    if not re.fullmatch(r"[0-9a-fA-F]{6}", valor):
        return None

    try:
        return discord.Color(int(valor, 16))
    except ValueError:
        return None


# ============================================================
# MODAL CREAR ROL
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
        label="URL de la imagen del ícono (Opcional)",
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
                "❌ Este sistema solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # CONTAR ROLES DEL USUARIO
        # ----------------------------------------------------

        data = cargar_roles()

        guild_data = data.get(str(guild.id), {})

        creados = guild_data.get(str(interaction.user.id), [])

        # Limpiar roles eliminados
        creados_validos = []

        for role_id in creados:
            role = guild.get_role(int(role_id))

            if role:
                creados_validos.append(role_id)

        creados = creados_validos

        if len(creados) >= MAX_ROLES_POR_USUARIO:
            return await interaction.response.send_message(
                f"❌ Ya tenés el máximo de **{MAX_ROLES_POR_USUARIO} "
                f"roles decorativos**.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------

        nombre = self.nombre.value.strip()

        if not nombre:
            return await interaction.response.send_message(
                "❌ El nombre no puede estar vacío.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # COLOR
        # ----------------------------------------------------

        color = convertir_color(self.color.value)

        if color is None:
            return await interaction.response.send_message(
                "❌ Color inválido.\n\n"
                "Usá un color HEX de 6 caracteres.\n"
                "Ejemplo: `#9B59B6`",
                ephemeral=True
            )

        # ----------------------------------------------------
        # ÍCONO DEL ROL
        # ----------------------------------------------------

        icon_bytes = None
        url = self.icono_url.value.strip()

        if url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            icon_bytes = await resp.read()
                        else:
                            return await interaction.response.send_message(
                                "❌ No se pudo descargar la imagen de la URL provista.",
                                ephemeral=True
                            )
            except Exception:
                return await interaction.response.send_message(
                    "❌ Error al conectar con la URL de la imagen.",
                    ephemeral=True
                )

        # ----------------------------------------------------
        # POSICIÓN DEL BOT
        # ----------------------------------------------------

        bot_member = guild.me

        if bot_member is None:
            return await interaction.response.send_message(
                "❌ No pude encontrar al bot en este servidor.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # CREAR ROL
        # ----------------------------------------------------

        try:

            role = await guild.create_role(
                name=nombre,
                color=color,
                display_icon=icon_bytes,

                # IMPORTANTE:
                # SIN PERMISOS DE MODERACIÓN
                permissions=discord.Permissions.none(),

                reason=f"Rol decorativo creado por {interaction.user}"
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No tengo permiso de **Gestionar roles** o el servidor no cuenta con Server Boost Nivel 2 para usar íconos.",
                ephemeral=True
            )

        except discord.HTTPException as e:

            return await interaction.response.send_message(
                f"❌ Discord rechazó la creación del rol.\n"
                f"`{e}`",
                ephemeral=True
            )

        # ----------------------------------------------------
        # GUARDAR
        # ----------------------------------------------------

        guild_data.setdefault(str(interaction.user.id), [])
        guild_data[str(interaction.user.id)].append(str(role.id))

        data[str(guild.id)] = guild_data

        guardar_roles(data)

        # ----------------------------------------------------
        # INTENTAR PONERLO DEBAJO DEL BOT
        # ----------------------------------------------------

        try:

            if bot_member.top_role.position > 1:

                posicion = max(1, bot_member.top_role.position - 1)

                await role.edit(
                    position=posicion
                )

        except (discord.Forbidden, discord.HTTPException):
            pass

        # ----------------------------------------------------
        # RESPUESTA
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🎨・rol creado",
            description=(
                f"Se creó correctamente tu rol decorativo.\n\n"
                f"**Nombre:** {role.mention}\n"
                f"**Color:** `{self.color.value}`\n"
                f"**Ícono:** {'Asignado' if icon_bytes else 'Sin ícono'}\n\n"
                f"Este rol no tiene ningún permiso de moderación."
            ),
            color=color
        )

        embed.set_footer(
            text="Podés compartirlo usando el botón de abajo."
        )

        await interaction.response.send_message(
            embed=embed,
            view=RolCreadoView(self.cog, role.id),
            ephemeral=True
        )


# ============================================================
# MODAL CAMBIAR COLOR
# ============================================================

class CambiarColorModal(discord.ui.Modal, title="🎨 Cambiar color"):

    color = discord.ui.TextInput(
        label="Nuevo color HEX",
        placeholder="Ej: #FF00FF",
        max_length=7,
        required=True
    )

    def __init__(self, cog, role_id):
        super().__init__()

        self.cog = cog
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ Ese rol ya no existe.",
                ephemeral=True
            )

        color = convertir_color(self.color.value)

        if color is None:
            return await interaction.response.send_message(
                "❌ Color inválido.\n"
                "Ejemplo: `#9B59B6`",
                ephemeral=True
            )

        if not self.cog.usuario_es_dueno(
            interaction.guild.id,
            interaction.user.id,
            self.role_id
        ):
            return await interaction.response.send_message(
                "❌ Ese rol no es tuyo.",
                ephemeral=True
            )

        try:

            await role.edit(
                color=color,
                reason=f"Color cambiado por {interaction.user}"
            )

        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No tengo permisos para editar ese rol.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"🎨 Color actualizado a `{self.color.value}`.",
            ephemeral=True
        )


# ============================================================
# MODAL CAMBIAR NOMBRE
# ============================================================

class CambiarNombreModal(discord.ui.Modal, title="✏️ Cambiar nombre"):

    nombre = discord.ui.TextInput(
        label="Nuevo nombre",
        placeholder="Ej: 💜・violet",
        max_length=MAX_NOMBRE,
        required=True
    )

    def __init__(self, cog, role_id):
        super().__init__()

        self.cog = cog
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ Ese rol ya no existe.",
                ephemeral=True
            )

        if not self.cog.usuario_es_dueno(
            interaction.guild.id,
            interaction.user.id,
            self.role_id
        ):
            return await interaction.response.send_message(
                "❌ Ese rol no es tuyo.",
                ephemeral=True
            )

        try:

            await role.edit(
                name=self.nombre.value.strip(),
                reason=f"Nombre cambiado por {interaction.user}"
            )

        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No tengo permisos para editar ese rol.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"✏️ Nombre cambiado a **{discord.utils.escape_markdown(self.nombre.value)}**.",
            ephemeral=True
        )


# ============================================================
# MODAL COMPARTIR
# ============================================================

class CompartirModal(discord.ui.Modal, title="🔗 Compartir rol"):

    mensaje = discord.ui.TextInput(
        label="Mensaje",
        placeholder="Ej: ¿Quién quiere mi rol? 💜",
        style=discord.TextStyle.paragraph,
        max_length=300,
        required=False
    )

    def __init__(self, cog, role_id):
        super().__init__()

        self.cog = cog
        self.role_id = role_id

    async def on_submit(self, interaction: discord.Interaction):

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ Ese rol ya no existe.",
                ephemeral=True
            )

        if not self.cog.usuario_es_dueno(
            interaction.guild.id,
            interaction.user.id,
            self.role_id
        ):
            return await interaction.response.send_message(
                "❌ Ese rol no es tuyo.",
                ephemeral=True
            )

        mensaje = self.mensaje.value.strip()

        if not mensaje:
            mensaje = "¿Quién quiere mi rol? 💜"

        embed = discord.Embed(
            title=f"{role.name}",
            description=(
                f"{mensaje}\n\n"
                f"Creado por {interaction.user.mention}\n\n"
                f"Presioná el botón de abajo para obtenerlo."
            ),
            color=role.color
        )

        embed.set_footer(
            text="Rol decorativo • Sin permisos de moderación"
        )

        await interaction.response.send_message(
            embed=embed,
            view=ObtenerRolView(self.cog, role.id)
        )


# ============================================================
# VIEW PARA OBTENER ROL
# ============================================================

class ObtenerRolView(discord.ui.View):

    def __init__(self, cog, role_id):
        super().__init__(timeout=None)

        self.cog = cog
        self.role_id = role_id

        self.add_item(
            ObtenerRolButton(cog, role_id)
        )


class ObtenerRolButton(discord.ui.Button):

    def __init__(self, cog, role_id):
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

        if role is None:
            return await interaction.response.send_message(
                "❌ Este rol ya no existe.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # COMPROBAR SI YA LO TIENE
        # ----------------------------------------------------

        if role in interaction.user.roles:

            return await interaction.response.send_message(
                "💜 Ya tenés este rol.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # COMPROBAR JERARQUÍA
        # ----------------------------------------------------

        if guild.me.top_role <= role:

            return await interaction.response.send_message(
                "❌ No puedo asignarte este rol porque está "
                "por encima de mi rol.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # DAR ROL
        # ----------------------------------------------------

        try:

            await interaction.user.add_roles(
                role,
                reason="Rol decorativo obtenido"
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No tengo permisos para darte este rol.",
                ephemeral=True
            )

        await interaction.response.send_message(
            f"🎨 Conseguido: {role.mention}",
            ephemeral=True
        )


# ============================================================
# VIEW ROL CREADO
# ============================================================

class RolCreadoView(discord.ui.View):

    def __init__(self, cog, role_id):
        super().__init__(timeout=300)

        self.cog = cog
        self.role_id = role_id

    # --------------------------------------------------------
    # COMPARTIR
    # --------------------------------------------------------

    @discord.ui.button(
        label="Compartir",
        emoji="🔗",
        style=discord.ButtonStyle.primary
    )
    async def compartir(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.cog.usuario_es_dueno(
            interaction.guild.id,
            interaction.user.id,
            self.role_id
        ):
            return await interaction.response.send_message(
                "❌ Este rol no es tuyo.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            CompartirModal(
                self.cog,
                self.role_id
            )
        )

    # --------------------------------------------------------
    # CAMBIAR COLOR
    # --------------------------------------------------------

    @discord.ui.button(
        label="Color",
        emoji="🎨",
        style=discord.ButtonStyle.secondary
    )
    async def cambiar_color(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.cog.usuario_es_dueno(
            interaction.guild.id,
            interaction.user.id,
            self.role_id
        ):
            return await interaction.response.send_message(
                "❌ Este rol no es tuyo.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            CambiarColorModal(
                self.cog,
                self.role_id
            )
        )

    # --------------------------------------------------------
    # CAMBIAR NOMBRE
    # --------------------------------------------------------

    @discord.ui.button(
        label="Nombre",
        emoji="✏️",
        style=discord.ButtonStyle.secondary
    )
    async def cambiar_nombre(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.cog.usuario_es_dueno(
            interaction.guild.id,
            interaction.user.id,
            self.role_id
        ):
            return await interaction.response.send_message(
                "❌ Este rol no es tuyo.",
                ephemeral=True
            )

        await interaction.response.send_modal(
            CambiarNombreModal(
                self.cog,
                self.role_id
            )
        )

    # --------------------------------------------------------
    # ELIMINAR
    # --------------------------------------------------------

    @discord.ui.button(
        label="Eliminar",
        emoji="🗑️",
        style=discord.ButtonStyle.danger
    )
    async def eliminar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.cog.usuario_es_dueno(
            interaction.guild.id,
            interaction.user.id,
            self.role_id
        ):
            return await interaction.response.send_message(
                "❌ Este rol no es tuyo.",
                ephemeral=True
            )

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ Ese rol ya no existe.",
                ephemeral=True
            )

        try:

            await role.delete(
                reason=f"Rol decorativo eliminado por {interaction.user}"
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No puedo eliminar ese rol.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # ELIMINAR DEL JSON
        # ----------------------------------------------------

        data = cargar_roles()

        guild_data = data.get(
            str(interaction.guild.id),
            {}
        )

        usuario_roles = guild_data.get(
            str(interaction.user.id),
            []
        )

        usuario_roles = [
            rid for rid in usuario_roles
            if int(rid) != self.role_id
        ]

        guild_data[str(interaction.user.id)] = usuario_roles

        data[str(interaction.guild.id)] = guild_data

        guardar_roles(data)

        await interaction.response.send_message(
            "🗑️ Rol decorativo eliminado correctamente.",
            ephemeral=True
        )


# ============================================================
# PANEL PRINCIPAL
# ============================================================

class RolesDecorativosView(discord.ui.View):

    def __init__(self, cog):
        super().__init__(timeout=None)

        self.cog = cog

    @discord.ui.button(
        label="Crear rol",
        emoji="🎨",
        style=discord.ButtonStyle.primary,
        custom_id="decorativos_crear"
    )
    async def crear(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_modal(
            CrearRolModal(self.cog)
        )


# ============================================================
# COG
# ============================================================

class RolesDecorativos(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ========================================================
    # COMPROBAR DUEÑO
    # ========================================================

    def usuario_es_dueno(
        self,
        guild_id,
        user_id,
        role_id
    ):

        data = cargar_roles()

        guild_data = data.get(
            str(guild_id),
            {}
        )

        roles = guild_data.get(
            str(user_id),
            []
        )

        return str(role_id) in [
            str(x) for x in roles
        ]

    # ========================================================
    # /rolesdecorativos
    # ========================================================

    @commands.hybrid_command(
        name="rolesdecorativos",
        description="Abre el sistema de roles decorativos."
    )
    async def rolesdecorativos(
        self,
        ctx: commands.Context
    ):

        embed = discord.Embed(
            title="🎨・roles decorativos",
            description=(
                "Creá tu propio rol totalmente personalizado.\n\n"
                "🎨 **Color personalizado**\n"
                "✏️ **Nombre personalizado**\n"
                "🔗 **Compartilo con otros**\n"
                "✨ **Sin permisos de moderación**\n\n"
                f"Cada usuario puede crear hasta "
                f"**{MAX_ROLES_POR_USUARIO} roles**.\n\n"
                "Presioná el botón de abajo para comenzar."
            ),
            color=discord.Color.from_rgb(
                155,
                89,
                182
            )
        )

        embed.set_footer(
            text="Roles decorativos • Personalizá tu perfil"
        )

        await ctx.send(
            embed=embed,
            view=RolesDecorativosView(self)
        )

    # ========================================================
    # LISTAR ROLES
    # ========================================================

    @commands.hybrid_command(
        name="misroles",
        description="Muestra tus roles decorativos."
    )
    async def misroles(
        self,
        ctx: commands.Context
    ):

        data = cargar_roles()

        guild_data = data.get(
            str(ctx.guild.id),
            {}
        )

        roles_ids = guild_data.get(
            str(ctx.author.id),
            []
        )

        roles = []

        for role_id in roles_ids:

            role = ctx.guild.get_role(
                int(role_id)
            )

            if role:
                roles.append(role)

        if not roles:

            return await ctx.send(
                "🎨 No tenés roles decorativos creados.",
                ephemeral=True
            )

        descripcion = ""

        for role in roles:

            descripcion += (
                f"{role.mention} — `{role.id}`\n"
            )

        embed = discord.Embed(
            title="🎨・mis roles",
            description=descripcion,
            color=discord.Color.from_rgb(
                155,
                89,
                182
            )
        )

        await ctx.send(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # LOAD
    # ========================================================

    async def cog_load(self):

        # Panel persistente
        self.bot.add_view(
            RolesDecorativosView(self)
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(
        RolesDecorativos(bot)
    )
