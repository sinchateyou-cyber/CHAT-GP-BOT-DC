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
# CARGAR JSON
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
# SELECT
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
        for emoji, nombre in datos["roles"].items():
            opciones.append(
                discord.SelectOption(
                    label=str(nombre),
                    value=str(nombre),
                    emoji=str(emoji)
                )
            )
        super().__init__(
            placeholder=datos.get(
                "descripcion",
                "Seleccioná una opción"
            )[:150],
            min_values=1,
            max_values=1,
            options=opciones,
            custom_id=f"reactionrole_{categoria}"
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        try:
            guild = interaction.guild
            if guild is None:
                await interaction.response.send_message(
                    "❌ Este sistema solo funciona en un servidor.",
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
            if not bot_member.guild_permissions.manage_roles:
                await interaction.response.send_message(
                    "❌ El bot no tiene el permiso "
                    "**Gestionar roles**.",
                    ephemeral=True
                )
                return
            if rol_seleccionado >= bot_member.top_role:
                await interaction.response.send_message(
                    "❌ El rol del bot debe estar por encima "
                    "del rol que querés asignar.",
                    ephemeral=True
                )
                return
            # =================================================
            # OBTENER ROLES DE LA CATEGORÍA
            # =================================================
            roles_categoria = []
            for nombre in self.datos[
                "roles"
            ].values():
                rol = discord.utils.get(
                    guild.roles,
                    name=str(nombre)
                )
                if rol:
                    roles_categoria.append(
                        rol
                    )
            # =================================================
            # QUITAR ROLES ANTERIORES
            # =================================================
            for rol in roles_categoria:
                if rol in miembro.roles:
                    if rol != rol_seleccionado:
                        await miembro.remove_roles(
                            rol,
                            reason=(
                                f"Cambio de rol: "
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
            # ASIGNAR
            # =================================================
            await miembro.add_roles(
                rol_seleccionado,
                reason=(
                    f"Reaction Role: "
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
                    "❌ No tengo permisos para modificar "
                    "ese rol.",
                    ephemeral=True
                )
        except Exception as e:
            print(
                "[ROLES] ❌ Error en botón:"
            )
            traceback.print_exc()
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al asignar el rol.",
                    ephemeral=True
                )
# ============================================================
# VIEW
# ============================================================
class RoleView(discord.ui.View):
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
class Roles(commands.Cog):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
        print(
            "[ROLES] Sistema cargado correctamente."
        )
    # ========================================================
    # GRUPO
    # ========================================================
    roles_group = app_commands.Group(
        name="roles",
        description="Sistema de roles"
    )
    # ========================================================
    # FUNCIÓN CREAR PANEL
    # ========================================================
    async def enviar_panel(
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
                f"❌ No existe la categoría `{categoria}` "
                "en `data/roles.json`.",
                ephemeral=True
            )
            return
        datos = categorias[
            categoria
        ]
        # =====================================================
        # CREAR ROLES
        # =====================================================
        creados = 0
        for nombre in datos[
            "roles"
        ].values():
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
                            "Sistema de Reaction Roles"
                        )
                    )
                    creados += 1
                except discord.Forbidden:
                    await interaction.followup.send(
                        "❌ No tengo permiso para crear roles.",
                        ephemeral=True
                    )
                    return
        # =====================================================
        # EMBED
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
                "Reaction Roles"
            )
        )
        # =====================================================
        # ENVIAR
        # =====================================================
        await interaction.channel.send(
            embed=embed,
            view=RoleView(
                categoria,
                datos
            )
        )
        await interaction.followup.send(
            f"✅ Panel **{datos['titulo']}** creado correctamente.\n"
            f"➕ Roles creados: **{creados}**",
            ephemeral=True
        )
    # ========================================================
    # /ROLES SETUP
    # ========================================================
    @roles_group.command(
        name="setup",
        description=(
            "Crear los paneles principales"
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
            categorias = [
                "genero",
                "pais",
                "dispositivo",
                "edad"
            ]
            for categoria in categorias:
                await self.enviar_panel(
                    interaction,
                    categoria
                )
            await interaction.followup.send(
                "✅ Todos los paneles principales "
                "fueron creados correctamente.",
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
            await self.enviar_panel(
                interaction,
                "colores"
            )
        except Exception:
            print(
                "[ROLES] ❌ ERROR EN /roles colores:"
            )
            traceback.print_exc()
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
        Roles(bot)
    )