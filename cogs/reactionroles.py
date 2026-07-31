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
ROLES_FILE = os.path.join(
    DATA_FOLDER,
    "roles.json"
)
# ============================================================
# CARGAR ROLES
# ============================================================
def cargar_roles():
    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )
    if not os.path.exists(
        ROLES_FILE
    ):
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
            return json.load(
                archivo
            )
    except Exception as error:
        print(
            f"[ROLES] ❌ Error leyendo roles.json: "
            f"{error}"
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
        for emoji, nombre_rol in datos.get(
            "roles",
            {}
        ).items():
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
        if not opciones:
            opciones.append(
                discord.SelectOption(
                    label="Sin opciones",
                    value="none"
                )
            )
        # ====================================================
        # IMPORTANTE
        # ====================================================
        # Este custom_id mantiene compatibilidad con los
        # paneles que ya estaban creados anteriormente.
        # ====================================================
        super().__init__(
            placeholder=datos.get(
                "descripcion",
                "Seleccioná una opción"
            )[:150],
            min_values=1,
            max_values=1,
            options=opciones,
            custom_id=(
                f"roles:{categoria}"
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
            if nombre_seleccionado == "none":
                await interaction.response.send_message(
                    "❌ Esta categoría no tiene "
                    "roles configurados.",
                    ephemeral=True
                )
                return
            rol_seleccionado = discord.utils.get(
                guild.roles,
                name=nombre_seleccionado
            )
            if rol_seleccionado is None:
                await interaction.response.send_message(
                    "❌ El rol seleccionado no existe "
                    "en este servidor.",
                    ephemeral=True
                )
                return
            bot_member = guild.me
            if bot_member is None:
                await interaction.response.send_message(
                    "❌ No pude encontrar al bot "
                    "en este servidor.",
                    ephemeral=True
                )
                return
            # =================================================
            # PERMISO MANAGE ROLES
            # =================================================
            if not bot_member.guild_permissions.manage_roles:
                await interaction.response.send_message(
                    "❌ El bot no tiene el permiso "
                    "**Gestionar roles**.",
                    ephemeral=True
                )
                return
            # =================================================
            # JERARQUÍA DEL ROL
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
            # BUSCAR ROLES DE LA CATEGORÍA
            # =================================================
            roles_categoria = []
            for nombre_rol in self.datos.get(
                "roles",
                {}
            ).values():
                rol = discord.utils.get(
                    guild.roles,
                    name=str(
                        nombre_rol
                    )
                )
                if rol is not None:
                    roles_categoria.append(
                        rol
                    )
            # =================================================
            # QUITAR ROLES ANTERIORES
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
                        "Cambio de Reaction Role - "
                        f"{self.categoria}"
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
            # ASIGNAR ROL
            # =================================================
            await miembro.add_roles(
                rol_seleccionado,
                reason=(
                    "Reaction Role seleccionado - "
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
                    "Revisá que el rol del bot esté "
                    "por encima de los roles de selección.",
                    ephemeral=True
                )
        except Exception as error:
            print(
                "[ROLES] ❌ Error procesando "
                "Reaction Role:"
            )
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al procesar "
                    "el rol.",
                    ephemeral=True
                )
# ============================================================
# VIEW PERSISTENTE
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
        description="Sistema de Reaction Roles"
    )
    # ========================================================
    # CREAR ROLES
    # ========================================================
    async def crear_roles(
        self,
        guild,
        datos
    ):
        roles_creados = 0
        for nombre_rol in datos.get(
            "roles",
            {}
        ).values():
            nombre_rol = str(
                nombre_rol
            )
            rol = discord.utils.get(
                guild.roles,
                name=nombre_rol
            )
            if rol is None:
                try:
                    await guild.create_role(
                        name=nombre_rol,
                        reason=(
                            "Sistema de "
                            "Reaction Roles"
                        )
                    )
                    roles_creados += 1
                except discord.Forbidden:
                    raise RuntimeError(
                        "El bot no tiene permisos "
                        "para crear roles."
                    )
        return roles_creados
    # ========================================================
    # CREAR PANEL
    # ========================================================
    async def crear_panel(
        self,
        guild,
        canal,
        categoria,
        datos
    ):
        roles_creados = await self.crear_roles(
            guild,
            datos
        )
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
                "Sistema de Reaction Roles"
            )
        )
        await canal.send(
            embed=embed,
            view=RoleView(
                categoria,
                datos
            )
        )
        return roles_creados
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
        await interaction.response.defer(
            ephemeral=True
        )
        try:
            config = cargar_roles()
            categorias = config.get(
                "categorias",
                {}
            )
            categorias_principales = [
                "genero",
                "pais",
                "dispositivo",
                "edad"
            ]
            paneles_creados = 0
            roles_creados = 0
            for categoria in categorias_principales:
                datos = categorias.get(
                    categoria
                )
                if not datos:
                    print(
                        f"[ROLES] ⚠️ Categoría "
                        f"'{categoria}' no encontrada."
                    )
                    continue
                nuevos_roles = await self.crear_panel(
                    interaction.guild,
                    interaction.channel,
                    categoria,
                    datos
                )
                roles_creados += nuevos_roles
                paneles_creados += 1
            await interaction.followup.send(
                "✅ **Paneles principales creados correctamente.**\n\n"
                f"📋 Paneles creados: "
                f"**{paneles_creados}**\n"
                f"➕ Roles nuevos: "
                f"**{roles_creados}**\n\n"
                "🎨 Para crear el panel de colores "
                "usá `/roles colores`.",
                ephemeral=True
            )
        except Exception as error:
            print(
                "[ROLES] ❌ ERROR EN /roles setup:"
            )
            traceback.print_exc()
            await interaction.followup.send(
                "❌ Ocurrió un error al crear "
                "los paneles principales.\n\n"
                f"Error: `{error}`\n\n"
                "Revisá la consola del bot.",
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
        await interaction.response.defer(
            ephemeral=True
        )
        try:
            config = cargar_roles()
            categorias = config.get(
                "categorias",
                {}
            )
            datos = categorias.get(
                "colores"
            )
            if not datos:
                await interaction.followup.send(
                    "❌ No existe la categoría "
                    "`colores` en `data/roles.json`.",
                    ephemeral=True
                )
                return
            roles_creados = await self.crear_panel(
                interaction.guild,
                interaction.channel,
                "colores",
                datos
            )
            await interaction.followup.send(
                "✅ **Panel de colores creado correctamente.**\n\n"
                f"🎨 Roles nuevos: "
                f"**{roles_creados}**",
                ephemeral=True
            )
        except Exception as error:
            print(
                "[ROLES] ❌ ERROR EN /roles colores:"
            )
            traceback.print_exc()
            await interaction.followup.send(
                "❌ Ocurrió un error al crear "
                "el panel de colores.\n\n"
                f"Error: `{error}`",
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