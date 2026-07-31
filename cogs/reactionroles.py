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
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(ROLES_FILE):
        print("[ROLES] ❌ No existe data/roles.json")
        return {}
    try:
        with open(
            ROLES_FILE,
            "r",
            encoding="utf-8"
        ) as archivo:
            return json.load(archivo)
    except Exception as e:
        print(
            f"[ROLES] ❌ Error leyendo roles.json: {e}"
        )
        return {}
# ============================================================
# SELECT DE ROLES
# ============================================================
class RoleSelect(discord.ui.Select):
    def __init__(
        self,
        categoria,
        datos
    ):
        self.categoria = categoria
        self.datos = datos
        opciones = []
        for emoji, nombre in datos.get(
            "roles",
            {}
        ).items():
            opciones.append(
                discord.SelectOption(
                    label=str(
                        nombre
                    ),
                    value=str(
                        nombre
                    ),
                    emoji=str(
                        emoji
                    )
                )
            )
        # =====================================================
        # IMPORTANTE
        # =====================================================
        # Mantenemos el mismo custom_id utilizado por los
        # paneles anteriores.
        #
        # Esto permite que los paneles que ya existen sigan
        # funcionando después de reiniciar el bot.
        # =====================================================
        super().__init__(
            placeholder=datos.get(
                "descripcion",
                "Seleccioná una opción"
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
            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message(
                    "❌ Este sistema solo funciona "
                    "en servidores.",
                    ephemeral=True
                )
                return
            miembro = guild.get_member(
                interaction.user.id
            )
            if miembro is None:
                await interaction.response.send_message(
                    "❌ No pude encontrar tu usuario.",
                    ephemeral=True
                )
                return
            nombre_seleccionado = self.values[0]
            rol_seleccionado = discord.utils.get(
                guild.roles,
                name=nombre_seleccionado
            )
            if rol_seleccionado is None:
                await interaction.response.send_message(
                    "❌ El rol seleccionado no existe.",
                    ephemeral=True
                )
                return
            bot_member = guild.me
            if bot_member is None:
                await interaction.response.send_message(
                    "❌ No pude encontrar al bot.",
                    ephemeral=True
                )
                return
            # =================================================
            # PERMISOS
            # =================================================
            if not bot_member.guild_permissions.manage_roles:
                await interaction.response.send_message(
                    "❌ El bot no tiene el permiso "
                    "**Gestionar roles**.",
                    ephemeral=True
                )
                return
            # =================================================
            # JERARQUÍA
            # =================================================
            if rol_seleccionado >= bot_member.top_role:
                await interaction.response.send_message(
                    "❌ No puedo asignar ese rol porque "
                    "está por encima o al mismo nivel "
                    "que mi rol.",
                    ephemeral=True
                )
                return
            # =================================================
            # ROLES DE ESTA CATEGORÍA
            # =================================================
            roles_categoria = []
            for nombre in self.datos.get(
                "roles",
                {}
            ).values():
                rol = discord.utils.get(
                    guild.roles,
                    name=str(nombre)
                )
                if rol is not None:
                    roles_categoria.append(
                        rol
                    )
            # =================================================
            # QUITAR ROL ANTERIOR
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
                        "Cambio de Reaction Role: "
                        f"{self.categoria}"
                    )
                )
            # =================================================
            # YA TIENE EL ROL
            # =================================================
            if rol_seleccionado in miembro.roles:
                await interaction.response.send_message(
                    f"ℹ️ Ya tenés el rol "
                    f"{rol_seleccionado.mention}.",
                    ephemeral=True
                )
                return
            # =================================================
            # ASIGNAR ROL
            # =================================================
            await miembro.add_roles(
                rol_seleccionado,
                reason=(
                    "Reaction Role seleccionado: "
                    f"{self.categoria}"
                )
            )
            await interaction.response.send_message(
                f"✅ Se te asignó "
                f"{rol_seleccionado.mention}.",
                ephemeral=True
            )
        except discord.Forbidden:
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Discord rechazó la operación. "
                    "Revisá los permisos y la posición "
                    "del rol del bot.",
                    ephemeral=True
                )
        except Exception:
            print(
                "[ROLES] ❌ ERROR AL ASIGNAR ROL:"
            )
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al asignar "
                    "el rol. Revisá la consola.",
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
        print(
            "[ROLES] Sistema de Reaction Roles "
            "cargado correctamente."
        )
    # ========================================================
    # GRUPO /ROLES
    # ========================================================
    roles_group = app_commands.Group(
        name="roles",
        description="Sistema de roles"
    )
    # ========================================================
    # CREAR PANEL
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
                "no existe en `data/roles.json`.",
                ephemeral=True
            )
            return
        datos = categorias[
            categoria
        ]
        # =====================================================
        # CREAR ROLES
        # =====================================================
        roles_creados = 0
        for nombre in datos.get(
            "roles",
            {}
        ).values():
            nombre = str(
                nombre
            )
            rol = discord.utils.get(
                interaction.guild.roles,
                name=nombre
            )
            if rol is None:
                try:
                    await interaction.guild.create_role(
                        name=nombre,
                        reason=(
                            "Sistema de "
                            "Reaction Roles"
                        )
                    )
                    roles_creados += 1
                except discord.Forbidden:
                    await interaction.followup.send(
                        "❌ No tengo permiso para "
                        "crear roles.",
                        ephemeral=True
                    )
                    return
        # =====================================================
        # EMBED
        # =====================================================
        embed = discord.Embed(
            title=datos.get(
                "titulo",
                categoria
            ),
            description=(
                f"{datos.get('descripcion', '')}\n\n"
                "👇 Seleccioná una opción.\n"
                "Podés cambiar tu selección "
                "cuando quieras."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Sistema de Reaction Roles"
        )
        # =====================================================
        # VIEW
        # =====================================================
        view = RoleView(
            categoria,
            datos
        )
        await interaction.channel.send(
            embed=embed,
            view=view
        )
        await interaction.followup.send(
            "✅ Panel creado correctamente.\n\n"
            f"📋 Categoría: **{categoria}**\n"
            f"➕ Roles nuevos: **{roles_creados}**",
            ephemeral=True
        )
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
            creados = 0
            for categoria in categorias_principales:
                config = cargar_roles()
                categorias = config.get(
                    "categorias",
                    {}
                )
                if categoria not in categorias:
                    continue
                datos = categorias[
                    categoria
                ]
                # =============================================
                # CREAR ROLES
                # =============================================
                for nombre in datos.get(
                    "roles",
                    {}
                ).values():
                    nombre = str(
                        nombre
                    )
                    rol = discord.utils.get(
                        interaction.guild.roles,
                        name=nombre
                    )
                    if rol is None:
                        await interaction.guild.create_role(
                            name=nombre,
                            reason=(
                                "Sistema de "
                                "Reaction Roles"
                            )
                        )
                        creados += 1
                # =============================================
                # ENVIAR PANEL
                # =============================================
                embed = discord.Embed(
                    title=datos.get(
                        "titulo",
                        categoria
                    ),
                    description=(
                        f"{datos.get('descripcion', '')}\n\n"
                        "👇 Seleccioná una opción.\n"
                        "Podés cambiar tu selección "
                        "cuando quieras."
                    ),
                    color=discord.Color.blurple()
                )
                embed.set_footer(
                    text=(
                        "Sistema de "
                        "Reaction Roles"
                    )
                )
                await interaction.channel.send(
                    embed=embed,
                    view=RoleView(
                        categoria,
                        datos
                    )
                )
            await interaction.followup.send(
                "✅ Paneles principales creados correctamente.\n\n"
                "👤 Género\n"
                "🌎 País\n"
                "📱 Dispositivo\n"
                "🎂 Edad\n\n"
                "🎨 Para crear solamente el panel "
                "de colores usá `/roles colores`.",
                ephemeral=True
            )
        except Exception:
            print(
                "[ROLES] ❌ ERROR EN /roles setup:"
            )
            traceback.print_exc()
            await interaction.followup.send(
                "❌ Ocurrió un error al crear "
                "los paneles principales. "
                "Revisá la consola.",
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
                "[ROLES] ❌ ERROR EN /roles colores:"
            )
            traceback.print_exc()
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ Ocurrió un error al crear "
                    "el panel de colores. "
                    "Revisá la consola.",
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