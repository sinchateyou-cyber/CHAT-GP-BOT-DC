import os
import json
import traceback
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
ROLES_FILE = os.path.join(DATA_FOLDER, "roles.json")
# ============================================================
# CARGAR ROLES
# ============================================================
def cargar_roles():
    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )
    if not os.path.exists(ROLES_FILE):
        print(
            "[ROLES] ❌ No existe data/roles.json"
        )
        return {}
    try:
        with open(
            ROLES_FILE,
            "r",
            encoding="utf-8"
        ) as archivo:
            datos = json.load(
                archivo
            )
        return datos
    except Exception as e:
        print(
            f"[ROLES] ❌ Error leyendo roles.json: {e}"
        )
        return {}
# ============================================================
# SELECT DE ROLES
# ============================================================
class RoleSelect(
    discord.ui.Select
):
    def __init__(
        self,
        categoria,
        datos
    ):
        self.categoria = categoria
        self.datos = datos
        opciones = []
        for emoji, nombre_rol in datos[
            "roles"
        ].items():
            opciones.append(
                discord.SelectOption(
                    label=str(
                        nombre_rol
                    ),
                    value=str(
                        nombre_rol
                    ),
                    emoji=str(
                        emoji
                    )
                )
            )
        super().__init__(
            placeholder=datos.get(
                "descripcion",
                "Seleccioná una opción."
            )[:150],
            min_values=1,
            max_values=1,
            options=opciones,
            custom_id=(
                f"reactionrole:{categoria}"
            )
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        try:
            if not interaction.guild:
                await interaction.response.send_message(
                    "❌ Este sistema solo funciona en servidores.",
                    ephemeral=True
                )
                return
            miembro = interaction.guild.get_member(
                interaction.user.id
            )
            if not miembro:
                await interaction.response.send_message(
                    "❌ No pude encontrar tu usuario.",
                    ephemeral=True
                )
                return
            nombre_rol = self.values[0]
            rol_seleccionado = discord.utils.get(
                interaction.guild.roles,
                name=nombre_rol
            )
            if not rol_seleccionado:
                await interaction.response.send_message(
                    "❌ Ese rol no existe. "
                    "Pedile a un administrador que ejecute "
                    "el comando correspondiente.",
                    ephemeral=True
                )
                return
            bot_member = interaction.guild.me
            if not bot_member:
                await interaction.response.send_message(
                    "❌ No pude encontrar al bot en el servidor.",
                    ephemeral=True
                )
                return
            if not bot_member.guild_permissions.manage_roles:
                await interaction.response.send_message(
                    "❌ No tengo el permiso **Gestionar roles**.",
                    ephemeral=True
                )
                return
            if rol_seleccionado >= bot_member.top_role:
                await interaction.response.send_message(
                    "❌ No puedo asignar ese rol porque está "
                    "por encima de mi rol.",
                    ephemeral=True
                )
                return
            # =================================================
            # BUSCAR ROLES DE LA CATEGORÍA
            # =================================================
            roles_categoria = []
            for nombre in self.datos[
                "roles"
            ].values():
                rol = discord.utils.get(
                    interaction.guild.roles,
                    name=str(
                        nombre
                    )
                )
                if rol:
                    roles_categoria.append(
                        rol
                    )
            # =================================================
            # QUITAR OTROS ROLES DE LA CATEGORÍA
            # =================================================
            roles_a_quitar = [
                rol
                for rol in roles_categoria
                if rol in miembro.roles
                and rol != rol_seleccionado
            ]
            if roles_a_quitar:
                await miembro.remove_roles(
                    *roles_a_quitar,
                    reason=(
                        f"Cambio de rol "
                        f"({self.categoria})"
                    )
                )
            # =================================================
            # SI YA TIENE EL ROL
            # =================================================
            if rol_seleccionado in miembro.roles:
                await interaction.response.send_message(
                    f"ℹ️ Ya tenés el rol "
                    f"{rol_seleccionado.mention}.",
                    ephemeral=True
                )
                return
            # =================================================
            # ASIGNAR
            # =================================================
            await miembro.add_roles(
                rol_seleccionado,
                reason=(
                    f"Rol seleccionado: "
                    f"{self.categoria}"
                )
            )
            await interaction.response.send_message(
                f"✅ Se te asignó "
                f"{rol_seleccionado.mention}.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Discord rechazó la operación. "
                "Revisá los permisos y la posición "
                "del rol del bot.",
                ephemeral=True
            )
        except Exception:
            traceback.print_exc()
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ Ocurrió un error al asignar el rol.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Ocurrió un error al asignar el rol.",
                    ephemeral=True
                )
# ============================================================
# VIEW
# ============================================================
class RoleView(
    discord.ui.View
):
    def __init__(
        self,
        categoria,
        datos
    ):
        super().__init__(
            timeout=None
        )
        self.add_item(
            RoleSelect(
                categoria,
                datos
            )
        )
# ============================================================
# COG
# ============================================================
class Roles(
    commands.Cog
):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
        self.config = cargar_roles()
        print(
            "[ROLES] Sistema cargado correctamente."
        )
    # ========================================================
    # GRUPO /ROLES
    # ========================================================
    roles_group = app_commands.Group(
        name="roles",
        description="Sistema de roles"
    )
    # ========================================================
    # FUNCIÓN PARA CREAR UN PANEL
    # ========================================================
    async def crear_panel(
        self,
        interaction,
        categoria
    ):
        config = cargar_roles()
        categorias = config.get(
            "categorias",
            {}
        )
        if categoria not in categorias:
            await interaction.followup.send(
                f"❌ La categoría `{categoria}` "
                f"no existe en `roles.json`.",
                ephemeral=True
            )
            return False
        datos = categorias[
            categoria
        ]
        # =====================================================
        # CREAR ROLES
        # =====================================================
        roles_creados = 0
        for nombre_rol in datos[
            "roles"
        ].values():
            nombre_rol = str(
                nombre_rol
            )
            rol = discord.utils.get(
                interaction.guild.roles,
                name=nombre_rol
            )
            if rol is None:
                try:
                    await interaction.guild.create_role(
                        name=nombre_rol,
                        reason=(
                            "Sistema de Reaction Roles"
                        )
                    )
                    roles_creados += 1
                except discord.Forbidden:
                    await interaction.followup.send(
                        "❌ No tengo permiso para crear roles.",
                        ephemeral=True
                    )
                    return False
        # =====================================================
        # COMPROBAR PERMISOS
        # =====================================================
        bot_member = interaction.guild.me
        if not bot_member.guild_permissions.manage_roles:
            await interaction.followup.send(
                "❌ Necesito el permiso "
                "**Gestionar roles**.",
                ephemeral=True
            )
            return False
        # =====================================================
        # CREAR EMBED
        # =====================================================
        embed = discord.Embed(
            title=datos[
                "titulo"
            ],
            description=(
                f"{datos['descripcion']}\n\n"
                "👇 Seleccioná una opción.\n"
                "Podés cambiar tu selección "
                "cuando quieras."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text=(
                "Sistema de Reaction Roles"
            )
        )
        # =====================================================
        # CREAR VIEW
        # =====================================================
        view = RoleView(
            categoria,
            datos
        )
        await interaction.channel.send(
            embed=embed,
            view=view
        )
        # Registrar View persistente
        self.bot.add_view(
            view
        )
        await interaction.followup.send(
            "✅ Panel creado correctamente.\n\n"
            f"🎭 Categoría: "
            f"**{datos['titulo']}**\n"
            f"➕ Roles nuevos: "
            f"**{roles_creados}**",
            ephemeral=True
        )
        return True
    # ========================================================
    # /ROLES SETUP
    # ========================================================
    @roles_group.command(
        name="setup",
        description=(
            "Crear los paneles principales "
            "de roles"
        )
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def roles_setup(
        self,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(
                ephemeral=True
            )
            categorias_principales = [
                "genero",
                "pais",
                "dispositivo",
                "edad"
            ]
            config = cargar_roles()
            categorias = config.get(
                "categorias",
                {}
            )
            for categoria in categorias_principales:
                if categoria not in categorias:
                    continue
                datos = categorias[
                    categoria
                ]
                # Crear roles
                for nombre in datos[
                    "roles"
                ].values():
                    nombre = str(
                        nombre
                    )
                    if not discord.utils.get(
                        interaction.guild.roles,
                        name=nombre
                    ):
                        await interaction.guild.create_role(
                            name=nombre,
                            reason=(
                                "Sistema de Reaction Roles"
                            )
                        )
                # Crear panel
                embed = discord.Embed(
                    title=datos[
                        "titulo"
                    ],
                    description=(
                        f"{datos['descripcion']}\n\n"
                        "👇 Seleccioná una opción.\n"
                        "Podés cambiar tu selección "
                        "cuando quieras."
                    ),
                    color=discord.Color.blurple()
                )
                embed.set_footer(
                    text=(
                        "Sistema de Reaction Roles"
                    )
                )
                view = RoleView(
                    categoria,
                    datos
                )
                await interaction.channel.send(
                    embed=embed,
                    view=view
                )
                self.bot.add_view(
                    view
                )
            await interaction.followup.send(
                "✅ Paneles principales creados correctamente.\n\n"
                "👤 Género\n"
                "🌎 País\n"
                "📱 Dispositivo\n"
                "🎂 Edad\n\n"
                "🎨 Para crear el panel de colores "
                "usá `/roles colores`.",
                ephemeral=True
            )
        except Exception as e:
            print(
                "[ROLES] ❌ Error en /roles setup:"
            )
            traceback.print_exc()
            await interaction.followup.send(
                "❌ Ocurrió un error al crear "
                "los paneles principales.",
                ephemeral=True
            )
    # ========================================================
    # /ROLES COLORES
    # ========================================================
    @roles_group.command(
        name="colores",
        description=(
            "Crear solamente el panel de colores"
        )
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def roles_colores(
        self,
        interaction: discord.Interaction
    ):
        try:
            await interaction.response.defer(
                ephemeral=True
            )
            await self.crear_panel(
                interaction,
                "colores"
            )
        except Exception:
            print(
                "[ROLES] ❌ Error en /roles colores:"
            )
            traceback.print_exc()
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ Ocurrió un error al crear "
                    "el panel de colores.",
                    ephemeral=True
                )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot
):
    await bot.add_cog(
        Roles(
            bot
        )
    )