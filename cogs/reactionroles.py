import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
ROLES_FILE = os.path.join(DATA_FOLDER, "roles.json")
# ============================================================
# CARGAR ROLES DESDE JSON
# ============================================================
def cargar_roles():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    if not os.path.exists(ROLES_FILE):
        return {}
    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except Exception as e:
        print(f"[ROLES] Error leyendo roles.json: {e}")
        return {}
# ============================================================
# SELECT DE ROLES
# ============================================================
class RoleSelect(discord.ui.Select):
    def __init__(self, categoria, datos):
        self.categoria = categoria
        self.datos = datos
        opciones = []
        for emoji, nombre_rol in datos["roles"].items():
            opciones.append(
                discord.SelectOption(
                    label=nombre_rol,
                    value=nombre_rol,
                    emoji=emoji
                )
            )
        super().__init__(
            placeholder=datos.get(
                "descripcion",
                "Seleccioná una opción"
            ),
            min_values=0,
            max_values=1,
            options=opciones,
            custom_id=f"roles:{categoria}"
        )
    async def callback(
        self,
        interaction: discord.Interaction
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este sistema solo funciona en servidores.",
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
        # OBTENER TODOS LOS ROLES DE ESTA CATEGORÍA
        # ====================================================
        roles_categoria = []
        for nombre_rol in self.datos["roles"].values():
            rol = discord.utils.get(
                interaction.guild.roles,
                name=nombre_rol
            )
            if rol:
                roles_categoria.append(rol)
        # ====================================================
        # QUITAR ROLES ANTERIORES
        # ====================================================
        roles_a_quitar = [
            rol
            for rol in roles_categoria
            if rol in miembro.roles
        ]
        if roles_a_quitar:
            try:
                await miembro.remove_roles(
                    *roles_a_quitar,
                    reason=f"Cambio de rol en categoría {self.categoria}"
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ No puedo modificar tus roles. "
                    "Revisá la posición del rol del bot.",
                    ephemeral=True
                )
                return
        # ====================================================
        # SI NO SE SELECCIONÓ NADA
        # ====================================================
        if not self.values:
            await interaction.response.send_message(
                f"✅ Se eliminaron tus roles de "
                f"**{self.datos['titulo']}**.",
                ephemeral=True
            )
            return
        # ====================================================
        # OBTENER ROL SELECCIONADO
        # ====================================================
        nombre_seleccionado = self.values[0]
        rol = discord.utils.get(
            interaction.guild.roles,
            name=nombre_seleccionado
        )
        # ====================================================
        # CREAR ROL SI NO EXISTE
        # ====================================================
        if rol is None:
            try:
                rol = await interaction.guild.create_role(
                    name=nombre_seleccionado,
                    reason="Sistema automático de roles"
                )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ No tengo permisos para crear roles.",
                    ephemeral=True
                )
                return
        # ====================================================
        # ASIGNAR ROL
        # ====================================================
        try:
            await miembro.add_roles(
                rol,
                reason=f"Rol seleccionado: {self.categoria}"
            )
            await interaction.response.send_message(
                f"✅ Se te asignó el rol {rol.mention}.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No puedo asignarte ese rol. "
                "El rol del bot debe estar por encima "
                "del rol que querés asignar.",
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
    def __init__(self, bot):
        self.bot = bot
        self.config = cargar_roles()
        print(
            "[ROLES] Sistema de roles cargado correctamente."
        )
    # ========================================================
    # /ROLES SETUP
    # ========================================================
    roles_group = app_commands.Group(
        name="roles",
        description="Sistema de roles del servidor"
    )
    @roles_group.command(
        name="setup",
        description="Crear el panel de selección de roles"
    )
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def roles_setup(
        self,
        interaction: discord.Interaction
    ):
        if not self.config:
            await interaction.response.send_message(
                "❌ No se pudo cargar `data/roles.json`.",
                ephemeral=True
            )
            return
        await interaction.response.defer(
            ephemeral=True
        )
        canal = interaction.channel
        # ====================================================
        # CREAR ROLES AUTOMÁTICAMENTE
        # ====================================================
        for categoria, datos in self.config.get(
            "categorias",
            {}
        ).items():
            for nombre_rol in datos["roles"].values():
                rol = discord.utils.get(
                    interaction.guild.roles,
                    name=nombre_rol
                )
                if rol is None:
                    try:
                        await interaction.guild.create_role(
                            name=nombre_rol,
                            reason="Configuración del sistema de roles"
                        )
                    except discord.Forbidden:
                        print(
                            f"[ROLES] No se pudo crear: {nombre_rol}"
                        )
        # ====================================================
        # ENVIAR PANELES
        # ====================================================
        for categoria, datos in self.config[
            "categorias"
        ].items():
            embed = discord.Embed(
                title=datos["titulo"],
                description=(
                    f"{datos['descripcion']}\n\n"
                    "Seleccioná una opción del menú."
                ),
                color=discord.Color.blurple()
            )
            embed.set_footer(
                text="Podés cambiar tu selección cuando quieras."
            )
            await canal.send(
                embed=embed,
                view=RoleView(
                    categoria,
                    datos
                )
            )
        await interaction.followup.send(
            "✅ Paneles de roles creados correctamente.",
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
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            mensaje = (
                "❌ Necesitás permisos de administrador "
                "para usar este comando."
            )
        else:
            print(
                f"[ROLES] Error: {error}"
            )
            mensaje = (
                "❌ Ocurrió un error al configurar "
                "el sistema de roles."
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
async def setup(bot):
    await bot.add_cog(
        Roles(bot)
    )