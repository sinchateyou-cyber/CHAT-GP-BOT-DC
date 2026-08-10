import discord
from discord.ext import commands
from discord import app_commands
import json
import os
ROLES_FILE = "data/roles.json"
# ============================================================
# CARGAR / GUARDAR
# ============================================================
def cargar_roles():
    if not os.path.exists(ROLES_FILE):
        return {}
    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}
def guardar_roles(data):
    os.makedirs("data", exist_ok=True)
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )
# ============================================================
# OBTENER ROL POR ID
# ============================================================
def obtener_rol(guild: discord.Guild, role_id):
    try:
        role_id = int(role_id)
    except (TypeError, ValueError):
        return None
    return guild.get_role(role_id)
# ============================================================
# SELECT DE ROLES
# ============================================================
class RoleSelect(discord.ui.Select):
    def __init__(self, categoria, titulo, opciones):
        self.categoria = categoria
        select_options = []
        for emoji, role_id in opciones.items():
            role = None
            try:
                role_id_int = int(role_id)
                # El guild todavía no está disponible acá,
                # por eso solo guardamos el ID.
            except (TypeError, ValueError):
                role_id_int = 0
            # El label será el ID temporalmente.
            # Luego el callback obtiene el rol real.
            select_options.append(
                discord.SelectOption(
                    label=str(role_id),
                    emoji=emoji,
                    value=str(role_id)
                )
            )
        if not select_options:
            raise ValueError(
                f"La categoría '{categoria}' no tiene roles configurados."
            )
        super().__init__(
            placeholder=f"Seleccioná tu {titulo.lower()}...",
            min_values=1,
            max_values=1,
            options=select_options
        )
    async def callback(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este menú solamente puede utilizarse dentro de un servidor.",
                ephemeral=True
            )
            return
        data = cargar_roles()
        guild_data = data.get(str(interaction.guild.id), {})
        categorias = guild_data.get("categorias", {})
        categoria_data = categorias.get(self.categoria, {})
        roles_config = categoria_data.get("roles", {})
        if not roles_config:
            await interaction.response.send_message(
                "❌ Esta categoría no tiene roles configurados.",
                ephemeral=True
            )
            return
        # ====================================================
        # ROL ELEGIDO
        # ====================================================
        selected_id = self.values[0]
        selected_role = obtener_rol(
            interaction.guild,
            selected_id
        )
        if selected_role is None:
            await interaction.response.send_message(
                f"❌ El rol con ID `{selected_id}` no existe en este servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # COMPROBAR JERARQUÍA DEL BOT
        # ====================================================
        me = interaction.guild.me
        if me is None:
            await interaction.response.send_message(
                "❌ No pude obtener la información del bot.",
                ephemeral=True
            )
            return
        if selected_role >= me.top_role:
            await interaction.response.send_message(
                "❌ No puedo asignar ese rol porque está por encima "
                "o al mismo nivel que mi rol más alto.",
                ephemeral=True
            )
            return
        # ====================================================
        # QUITAR LOS DEMÁS ROLES DE LA CATEGORÍA
        # ====================================================
        roles_to_remove = []
        for role_id in roles_config.values():
            role = obtener_rol(
                interaction.guild,
                role_id
            )
            if role is None:
                continue
            if role == selected_role:
                continue
            if role in interaction.user.roles:
                roles_to_remove.append(role)
        try:
            if roles_to_remove:
                await interaction.user.remove_roles(
                    *roles_to_remove,
                    reason=f"Cambio de rol en categoría: {self.categoria}"
                )
            # =================================================
            # ASIGNAR ROL
            # =================================================
            if selected_role not in interaction.user.roles:
                await interaction.user.add_roles(
                    selected_role,
                    reason=f"Role Select: {self.categoria}"
                )
                mensaje = (
                    f"✅ **Rol asignado correctamente.**\n"
                    f"🎭 {selected_role.mention}"
                )
            else:
                mensaje = (
                    f"ℹ️ Ya tenés asignado el rol "
                    f"{selected_role.mention}."
                )
            await interaction.response.send_message(
                mensaje,
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para modificar tus roles.",
                ephemeral=True
            )
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Discord rechazó la modificación del rol. "
                "Probá nuevamente.",
                ephemeral=True
            )
# ============================================================
# VIEW
# ============================================================
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
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este comando solamente puede utilizarse en un servidor.",
                ephemeral=True
            )
            return
        data = cargar_roles()
        guild_id = str(interaction.guild.id)
        if guild_id not in data:
            await interaction.response.send_message(
                "❌ Este servidor todavía no tiene roles configurados.",
                ephemeral=True
            )
            return
        categorias = data[guild_id].get("categorias", {})
        if not categorias:
            await interaction.response.send_message(
                "❌ No hay categorías de roles configuradas.",
                ephemeral=True
            )
            return
        # ====================================================
        # EMBED PRINCIPAL
        # ====================================================
        embed = discord.Embed(
            title="✦ 𝐑𝐎𝐋𝐄𝐒 𝐃𝐄𝐋 𝐒𝐄𝐑𝐕𝐈𝐃𝐎𝐑 ✦",
            description=(
                "**Elegí tus roles utilizando los menús de abajo.**\n"
                "Podés cambiarlos cuando quieras.\n\n"
                "🟣 **Los roles se asignan automáticamente.**"
            ),
            color=discord.Color.from_rgb(
                145,
                70,
                255
            )
        )
        embed.set_footer(
            text=f"{interaction.guild.name} • Sistema de roles"
        )
        await interaction.response.send_message(
            embed=embed
        )
        # ====================================================
        # CREAR PANELES
        # ====================================================
        for categoria, config in categorias.items():
            titulo = config.get(
                "titulo",
                categoria
            )
            descripcion = config.get(
                "descripcion",
                ""
            )
            opciones = config.get(
                "roles",
                {}
            )
            if not opciones:
                continue
            # Crear opciones mostrando el nombre REAL
            # del rol en Discord.
            select_options = []
            for emoji, role_id in opciones.items():
                role = obtener_rol(
                    interaction.guild,
                    role_id
                )
                if role is None:
                    continue
                select_options.append(
                    discord.SelectOption(
                        label=role.name[:100],
                        emoji=emoji,
                        value=str(role.id)
                    )
                )
            if not select_options:
                continue
            select = discord.ui.Select(
                placeholder=f"Seleccioná tu {titulo.lower()}...",
                min_values=1,
                max_values=1,
                options=select_options
            )
            async def select_callback(
                select_interaction: discord.Interaction,
                select=select,
                categoria=categoria,
                opciones=opciones
            ):
                selected_id = select.values[0]
                selected_role = obtener_rol(
                    select_interaction.guild,
                    selected_id
                )
                if selected_role is None:
                    await select_interaction.response.send_message(
                        "❌ Ese rol ya no existe.",
                        ephemeral=True
                    )
                    return
                me = select_interaction.guild.me
                if me is None or selected_role >= me.top_role:
                    await select_interaction.response.send_message(
                        "❌ No puedo asignar ese rol porque está por encima "
                        "de mi rol más alto.",
                        ephemeral=True
                    )
                    return
                # Quitar roles de esta categoría
                for role_id in opciones.values():
                    role = obtener_rol(
                        select_interaction.guild,
                        role_id
                    )
                    if (
                        role
                        and role != selected_role
                        and role in select_interaction.user.roles
                    ):
                        try:
                            await select_interaction.user.remove_roles(
                                role,
                                reason=f"Cambio de rol: {categoria}"
                            )
                        except discord.Forbidden:
                            pass
                try:
                    if selected_role not in select_interaction.user.roles:
                        await select_interaction.user.add_roles(
                            selected_role,
                            reason=f"Role Select: {categoria}"
                        )
                        await select_interaction.response.send_message(
                            f"✅ **Rol asignado:** {selected_role.mention}",
                            ephemeral=True
                        )
                    else:
                        await select_interaction.response.send_message(
                            f"ℹ️ Ya tenés {selected_role.mention}.",
                            ephemeral=True
                        )
                except discord.Forbidden:
                    await select_interaction.response.send_message(
                        "❌ No tengo permisos para asignarte ese rol.",
                        ephemeral=True
                    )
                except discord.HTTPException:
                    await select_interaction.response.send_message(
                        "❌ Ocurrió un error al modificar el rol.",
                        ephemeral=True
                    )
            select.callback = select_callback
            view = discord.ui.View(
                timeout=None
            )
            view.add_item(select)
            contenido = f"**{titulo}**"
            if descripcion:
                contenido += f"\n{descripcion}"
            await interaction.channel.send(
                contenido,
                view=view
            )
    # ========================================================
    # /CREAR_ROLES
    # ========================================================
    @app_commands.command(
        name="crear_roles",
        description="Crea los roles que todavía no existen."
    )
    @app_commands.checks.has_permissions(
        manage_roles=True
    )
    async def crear_roles(
        self,
        interaction: discord.Interaction
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este comando solamente funciona en un servidor.",
                ephemeral=True
            )
            return
        data = cargar_roles()
        guild_id = str(
            interaction.guild.id
        )
        if guild_id not in data:
            await interaction.response.send_message(
                "❌ No hay configuración para este servidor.",
                ephemeral=True
            )
            return
        categorias = data[guild_id].get(
            "categorias",
            {}
        )
        creados = 0
        existentes = 0
        for config in categorias.values():
            roles = config.get(
                "roles",
                {}
            )
            for role_id in roles.values():
                # Si ya existe por ID
                try:
                    role = interaction.guild.get_role(
                        int(role_id)
                    )
                except (TypeError, ValueError):
                    role = None
                if role:
                    existentes += 1
                    continue
                # Con IDs no podemos saber el nombre del rol
                # si el rol todavía no existe.
                #
                # Por eso no creamos roles automáticamente
                # desde este comando.
        await interaction.response.send_message(
            (
                f"ℹ️ **Sistema basado en IDs**\n\n"
                f"🎭 Roles encontrados: `{existentes}`\n"
                f"➕ Roles creados: `{creados}`\n\n"
                f"Los IDs deben corresponder a roles que ya existan "
                f"en el servidor."
            ),
            ephemeral=True
        )
    # ========================================================
    # ERROR HANDLER
    # ========================================================
    @roles.error
    async def roles_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Necesitás **Gestionar roles** para usar este comando.",
                    ephemeral=True
                )
        else:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al ejecutar `/roles`.",
                    ephemeral=True
                )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        ReactionRoles(bot)
    )