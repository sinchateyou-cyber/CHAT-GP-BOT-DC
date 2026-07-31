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
# CARGAR CONFIGURACIÓN
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
            datos = json.load(archivo)
        if not isinstance(datos, dict):
            print("[ROLES] ❌ roles.json no contiene un objeto válido.")
            return {}
        if "categorias" not in datos:
            print("[ROLES] ❌ Falta la clave 'categorias' en roles.json.")
            return {}
        return datos
    except json.JSONDecodeError as e:
        print(
            f"[ROLES] ❌ Error JSON en roles.json: {e}"
        )
        return {}
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
        for emoji, nombre_rol in datos.get(
            "roles",
            {}
        ).items():
            opciones.append(
                discord.SelectOption(
                    label=str(nombre_rol),
                    value=str(nombre_rol),
                    emoji=str(emoji)
                )
            )
        if not opciones:
            raise ValueError(
                f"La categoría '{categoria}' no tiene roles."
            )
        super().__init__(
            placeholder=datos.get(
                "descripcion",
                "Seleccioná una opción"
            )[:150],
            min_values=1,
            max_values=1,
            options=opciones,
            custom_id=f"reactionrole:{categoria}"
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        try:
            if interaction.guild is None:
                await interaction.response.send_message(
                    "❌ Este sistema solo funciona dentro de un servidor.",
                    ephemeral=True
                )
                return
            miembro = interaction.guild.get_member(
                interaction.user.id
            )
            if miembro is None:
                await interaction.response.send_message(
                    "❌ No pude encontrar tu usuario.",
                    ephemeral=True
                )
                return
            # ====================================================
            # ROL SELECCIONADO
            # ====================================================
            nombre_seleccionado = self.values[0]
            rol_seleccionado = discord.utils.get(
                interaction.guild.roles,
                name=nombre_seleccionado
            )
            if rol_seleccionado is None:
                await interaction.response.send_message(
                    "❌ Ese rol no existe. "
                    "Pedile a un administrador que vuelva a ejecutar "
                    "`/roles setup`.",
                    ephemeral=True
                )
                return
            # ====================================================
            # COMPROBAR JERARQUÍA DEL BOT
            # ====================================================
            bot_member = interaction.guild.me
            if bot_member is None:
                await interaction.response.send_message(
                    "❌ No pude obtener la información del bot.",
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
                    "por encima o al mismo nivel que mi rol.\n\n"
                    "Subí el rol del bot por encima de los roles "
                    "de reacción.",
                    ephemeral=True
                )
                return
            # ====================================================
            # BUSCAR ROLES DE LA MISMA CATEGORÍA
            # ====================================================
            roles_categoria = []
            for nombre_rol in self.datos.get(
                "roles",
                {}
            ).values():
                rol = discord.utils.get(
                    interaction.guild.roles,
                    name=str(nombre_rol)
                )
                if rol is not None:
                    roles_categoria.append(
                        rol
                    )
            # ====================================================
            # QUITAR EL ROL ANTERIOR
            # ====================================================
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
                        f"Cambio de rol de reacción: "
                        f"{self.categoria}"
                    )
                )
            # ====================================================
            # SI YA TIENE EL ROL
            # ====================================================
            if rol_seleccionado in miembro.roles:
                await interaction.response.send_message(
                    f"ℹ️ Ya tenés el rol {rol_seleccionado.mention}.",
                    ephemeral=True
                )
                return
            # ====================================================
            # ASIGNAR ROL
            # ====================================================
            await miembro.add_roles(
                rol_seleccionado,
                reason=(
                    f"Rol de reacción seleccionado: "
                    f"{self.categoria}"
                )
            )
            await interaction.response.send_message(
                f"✅ Se te asignó el rol "
                f"{rol_seleccionado.mention}.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Discord rechazó la operación.\n\n"
                "Revisá que el bot tenga **Gestionar roles** "
                "y que su rol esté por encima de los roles "
                "de reacción.",
                ephemeral=True
            )
        except Exception as e:
            print(
                f"[ROLES] ❌ Error en selección:"
            )
            traceback.print_exc()
            if interaction.response.is_done():
                await interaction.followup.send(
                    "❌ Ocurrió un error al asignar el rol. "
                    "Revisá la consola del bot.",
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "❌ Ocurrió un error al asignar el rol. "
                    "Revisá la consola del bot.",
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
        self.config = cargar_roles()
        print(
            "[ROLES] Sistema de roles cargado."
        )
    # ========================================================
    # GRUPO /ROLES
    # ========================================================
    roles_group = app_commands.Group(
        name="roles",
        description="Sistema de roles por selección"
    )
    # ========================================================
    # /ROLES SETUP
    # ========================================================
    @roles_group.command(
        name="setup",
        description="Crear el sistema de roles"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def roles_setup(
        self,
        interaction: discord.Interaction
    ):
        try:
            # =================================================
            # VALIDAR SERVIDOR
            # =================================================
            if interaction.guild is None:
                await interaction.response.send_message(
                    "❌ Este comando solo funciona en un servidor.",
                    ephemeral=True
                )
                return
            # =================================================
            # RECARGAR JSON
            # =================================================
            self.config = cargar_roles()
            if not self.config:
                await interaction.response.send_message(
                    "❌ No se pudo cargar `data/roles.json`.",
                    ephemeral=True
                )
                return
            categorias = self.config.get(
                "categorias",
                {}
            )
            if not categorias:
                await interaction.response.send_message(
                    "❌ No hay categorías configuradas "
                    "en `data/roles.json`.",
                    ephemeral=True
                )
                return
            # =================================================
            # RESPONDER ANTES DE PROCESAR
            # =================================================
            await interaction.response.defer(
                ephemeral=True
            )
            # =================================================
            # COMPROBAR PERMISOS DEL BOT
            # =================================================
            bot_member = interaction.guild.me
            if bot_member is None:
                await interaction.followup.send(
                    "❌ No pude obtener la información del bot.",
                    ephemeral=True
                )
                return
            if not bot_member.guild_permissions.manage_roles:
                await interaction.followup.send(
                    "❌ El bot no tiene el permiso "
                    "**Gestionar roles**.",
                    ephemeral=True
                )
                return
            # =================================================
            # CREAR ROLES
            # =================================================
            roles_creados = []
            roles_existentes = []
            for categoria, datos in categorias.items():
                roles = datos.get(
                    "roles",
                    {}
                )
                for nombre_rol in roles.values():
                    nombre_rol = str(
                        nombre_rol
                    )
                    rol = discord.utils.get(
                        interaction.guild.roles,
                        name=nombre_rol
                    )
                    if rol is None:
                        try:
                            rol = await interaction.guild.create_role(
                                name=nombre_rol,
                                reason=(
                                    "Sistema de roles "
                                    "por selección"
                                )
                            )
                            roles_creados.append(
                                nombre_rol
                            )
                        except discord.Forbidden:
                            await interaction.followup.send(
                                "❌ No puedo crear roles.\n\n"
                                "Verificá que el bot tenga "
                                "**Gestionar roles**.",
                                ephemeral=True
                            )
                            return
                    else:
                        roles_existentes.append(
                            nombre_rol
                        )
            # =================================================
            # ACTUALIZAR LISTA DE ROLES
            # =================================================
            # Discord puede tardar un instante en reflejar
            # los roles recién creados.
            await interaction.guild.fetch_roles()
            # =================================================
            # ENVIAR PANELES
            # =================================================
            canal = interaction.channel
            if canal is None:
                await interaction.followup.send(
                    "❌ No pude encontrar el canal actual.",
                    ephemeral=True
                )
                return
            paneles_creados = 0
            for categoria, datos in categorias.items():
                titulo = datos.get(
                    "titulo",
                    categoria
                )
                descripcion = datos.get(
                    "descripcion",
                    "Seleccioná una opción."
                )
                embed = discord.Embed(
                    title=titulo,
                    description=(
                        f"{descripcion}\n\n"
                        "👇 Elegí una opción del menú.\n"
                        "Podés cambiar tu selección "
                        "cuando quieras."
                    ),
                    color=discord.Color.blurple()
                )
                embed.set_footer(
                    text=(
                        "Sistema de roles • "
                        "Seleccioná una opción"
                    )
                )
                try:
                    view = RoleView(
                        categoria,
                        datos
                    )
                    await canal.send(
                        embed=embed,
                        view=view
                    )
                    # Registrar view persistente
                    self.bot.add_view(
                        view
                    )
                    paneles_creados += 1
                except Exception as e:
                    print(
                        f"[ROLES] ❌ Error creando panel "
                        f"{categoria}: {e}"
                    )
                    traceback.print_exc()
            # =================================================
            # RESULTADO
            # =================================================
            await interaction.followup.send(
                "✅ **Sistema de roles configurado.**\n\n"
                f"📋 Paneles creados: "
                f"**{paneles_creados}**\n"
                f"➕ Roles creados: "
                f"**{len(roles_creados)}**\n\n"
                "Los usuarios ya pueden seleccionar "
                "sus roles.",
                ephemeral=True
            )
        except Exception as e:
            print(
                "\n[ROLES] ❌ ERROR COMPLETO:"
            )
            traceback.print_exc()
            mensaje = (
                "❌ Ocurrió un error al configurar "
                "el sistema de roles.\n\n"
                "Revisá la consola del bot para "
                "ver el error exacto."
            )
            if interaction.response.is_done():
                await interaction.followup.send(
                    mensaje,
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    mensaje,
                    ephemeral=True
                )
    # ========================================================
    # ERROR DEL COMANDO
    # ========================================================
    @roles_setup.error
    async def roles_setup_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        print(
            "\n[ROLES] ❌ ERROR DEL COMANDO:"
        )
        traceback.print_exception(
            type(error),
            error,
            error.__traceback__
        )
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            mensaje = (
                "❌ Necesitás permisos de administrador "
                "para usar `/roles setup`."
            )
        else:
            mensaje = (
                "❌ Error al ejecutar `/roles setup`.\n"
                "Revisá la consola del bot."
            )
        if interaction.response.is_done():
            await interaction.followup.send(
                mensaje,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                mensaje,
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