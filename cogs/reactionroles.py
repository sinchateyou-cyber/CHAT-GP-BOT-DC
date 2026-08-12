import discord
from discord.ext import commands
from discord import app_commands

import json
import os


ROLES_FILE = "data/roles.json"


# ============================================================
# CARGAR
# ============================================================

def cargar_roles():

    if not os.path.exists(ROLES_FILE):
        return {}

    try:

        with open(
            ROLES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as error:

        print(
            f"[ROLES] Error leyendo roles.json: {error}"
        )

        return {}


# ============================================================
# OBTENER ROL
# ============================================================

def obtener_rol(
    guild: discord.Guild,
    role_id
):

    try:

        role_id = int(role_id)

    except (
        TypeError,
        ValueError
    ):

        return None

    return guild.get_role(role_id)


# ============================================================
# CUSTOM ID
# ============================================================

def custom_id(
    guild_id,
    categoria
):

    return (
        f"reactionroles:"
        f"{guild_id}:"
        f"{categoria}"
    )


# ============================================================
# PROCESAR ROL
# ============================================================

async def procesar_rol(
    interaction: discord.Interaction,
    categoria: str,
    opciones: dict
):

    if interaction.guild is None:

        await interaction.response.send_message(
            "❌ Este menú solo funciona dentro de un servidor.",
            ephemeral=True
        )

        return

    if not interaction.values:

        await interaction.response.send_message(
            "❌ No seleccionaste ningún rol.",
            ephemeral=True
        )

        return

    selected_id = interaction.values[0]

    role = obtener_rol(
        interaction.guild,
        selected_id
    )

    if role is None:

        await interaction.response.send_message(
            "❌ Ese rol ya no existe.",
            ephemeral=True
        )

        return

    # ========================================================
    # BOT
    # ========================================================

    me = interaction.guild.me

    if me is None:

        try:

            me = await interaction.guild.fetch_member(
                interaction.client.user.id
            )

        except Exception:

            await interaction.response.send_message(
                "❌ No pude obtener la información del bot.",
                ephemeral=True
            )

            return

    # ========================================================
    # ADMINISTRADOR
    # ========================================================

    if role.is_default():

        await interaction.response.send_message(
            "❌ No podés seleccionar el rol @everyone.",
            ephemeral=True
        )

        return

    # ========================================================
    # JERARQUÍA
    # ========================================================

    if role >= me.top_role:

        await interaction.response.send_message(
            (
                "❌ **No puedo darte ese rol.**\n\n"
                f"El rol {role.mention} está por encima "
                "o al mismo nivel que mi rol."
            ),
            ephemeral=True
        )

        return

    # ========================================================
    # PERMISOS
    # ========================================================

    if not me.guild_permissions.manage_roles:

        await interaction.response.send_message(
            "❌ El bot no tiene el permiso **Gestionar roles**.",
            ephemeral=True
        )

        return

    # ========================================================
    # ROLES DE ESTA CATEGORÍA
    # ========================================================

    quitar = []

    for role_id in opciones.values():

        other_role = obtener_rol(
            interaction.guild,
            role_id
        )

        if other_role is None:
            continue

        if other_role == role:
            continue

        if other_role in interaction.user.roles:

            quitar.append(
                other_role
            )

    # ========================================================
    # SI YA LO TIENE
    # ========================================================

    try:

        if role in interaction.user.roles:

            # Lo dejamos asignado.
            # No lo removemos al volver a tocarlo.

            if quitar:

                await interaction.user.remove_roles(
                    *quitar,
                    reason=(
                        f"Reaction Roles "
                        f"{categoria}"
                    )
                )

            await interaction.response.send_message(
                (
                    "ℹ️ Ya tenés asignado "
                    f"{role.mention}."
                ),
                ephemeral=True
            )

            return

        # ====================================================
        # QUITAR OTROS
        # ====================================================

        if quitar:

            await interaction.user.remove_roles(
                *quitar,
                reason=(
                    f"Reaction Roles "
                    f"{categoria}"
                )
            )

        # ====================================================
        # AGREGAR
        # ====================================================

        await interaction.user.add_roles(
            role,
            reason=(
                f"Reaction Roles "
                f"{categoria}"
            )
        )

        await interaction.response.send_message(
            (
                "✅ **Rol asignado correctamente.**\n\n"
                f"🎭 {role.mention}"
            ),
            ephemeral=True
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            (
                "❌ Discord rechazó la modificación.\n\n"
                "Revisá que el bot tenga "
                "**Gestionar roles** y que su rol esté "
                "por encima de los roles configurados."
            ),
            ephemeral=True
        )

    except discord.HTTPException as error:

        print(
            f"[ROLES] HTTP ERROR: {error}"
        )

        await interaction.response.send_message(
            "❌ Discord rechazó la operación.",
            ephemeral=True
        )

    except Exception as error:

        print(
            f"[ROLES] ERROR: {error}"
        )

        await interaction.response.send_message(
            "❌ Ocurrió un error al asignar el rol.",
            ephemeral=True
        )


# ============================================================
# SELECT
# ============================================================

class RoleSelect(
    discord.ui.Select
):

    def __init__(
        self,
        categoria,
        titulo,
        opciones,
        guild
    ):

        self.categoria = categoria
        self.guild_id = guild.id

        select_options = []

        for emoji, role_id in opciones.items():

            role = obtener_rol(
                guild,
                role_id
            )

            if role is None:

                print(
                    f"[ROLES] Rol inexistente: "
                    f"{role_id}"
                )

                continue

            if len(select_options) >= 25:
                break

            try:

                option = discord.SelectOption(
                    label=role.name[:100],
                    value=str(role.id),
                    emoji=emoji
                )

            except Exception:

                option = discord.SelectOption(
                    label=role.name[:100],
                    value=str(role.id)
                )

            select_options.append(
                option
            )

        if not select_options:

            raise ValueError(
                f"La categoría {categoria} "
                "no tiene roles válidos."
            )

        super().__init__(
            placeholder=(
                f"Seleccioná "
                f"{titulo.replace('*', '').lower()}..."
            )[:150],

            min_values=1,
            max_values=1,

            options=select_options,

            custom_id=custom_id(
                guild.id,
                categoria
            )
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        print(
            f"[ROLES] Selección recibida: "
            f"{interaction.user} "
            f"→ {self.categoria}"
        )

        data = cargar_roles()

        guild_data = data.get(
            str(interaction.guild.id),
            {}
        )

        categorias = guild_data.get(
            "categorias",
            {}
        )

        categoria_data = categorias.get(
            self.categoria,
            {}
        )

        opciones = categoria_data.get(
            "roles",
            {}
        )

        if not opciones:

            await interaction.response.send_message(
                "❌ Esta categoría no tiene roles configurados.",
                ephemeral=True
            )

            return

        await procesar_rol(
            interaction,
            self.categoria,
            opciones
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
        titulo,
        opciones,
        guild
    ):

        super().__init__(
            timeout=None
        )

        self.add_item(
            RoleSelect(
                categoria,
                titulo,
                opciones,
                guild
            )
        )


# ============================================================
# COG
# ============================================================

class ReactionRoles(
    commands.Cog
):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        print(
            "🎭 [REACTION ROLES] Sistema iniciado."
        )

    # ========================================================
    # READY
    # ========================================================

    @commands.Cog.listener()
    async def on_ready(self):

        # Evitamos registrar todo varias veces
        if getattr(
            self,
            "_views_registered",
            False
        ):

            return

        self._views_registered = True

        print(
            "🎭 [REACTION ROLES] Registrando views..."
        )

        await self.registrar_views()

    # ========================================================
    # REGISTRAR VIEWS
    # ========================================================

    async def registrar_views(self):

        data = cargar_roles()

        guild_data = data.get(
            str(self.bot.guilds[0].id),
            {}
        ) if self.bot.guilds else {}

        # ====================================================
        # USAR GUILD PRINCIPAL
        # ====================================================

        guild = self.bot.get_guild(
            1534290216418938891
        )

        if guild is None:

            print(
                "❌ [ROLES] No encontré el servidor."
            )

            return

        guild_data = data.get(
            str(guild.id),
            {}
        )

        categorias = guild_data.get(
            "categorias",
            {}
        )

        if not categorias:

            print(
                "⚠️ [ROLES] No hay categorías."
            )

            return

        cantidad = 0

        for categoria, config in categorias.items():

            titulo = config.get(
                "titulo",
                categoria
            )

            opciones = config.get(
                "roles",
                {}
            )

            if not opciones:
                continue

            try:

                view = RoleView(
                    categoria,
                    titulo,
                    opciones,
                    guild
                )

                self.bot.add_view(
                    view
                )

                cantidad += 1

                print(
                    f"✅ [ROLES] View: "
                    f"{categoria}"
                )

            except Exception as error:

                print(
                    f"❌ [ROLES] "
                    f"{categoria}: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        print(
            f"🎭 [ROLES] "
            f"{cantidad} views registradas."
        )

    # ========================================================
    # /ROLES
    # ========================================================

    @app_commands.command(
        name="roles",
        description="Envía el panel de selección de roles."
    )
    @app_commands.checks.has_permissions(
        manage_roles=True
    )
    async def roles(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este comando solo funciona en servidores.",
                ephemeral=True
            )

            return

        data = cargar_roles()

        guild_data = data.get(
            str(interaction.guild.id)
        )

        if not guild_data:

            await interaction.response.send_message(
                "❌ Este servidor no está configurado en roles.json.",
                ephemeral=True
            )

            return

        categorias = guild_data.get(
            "categorias",
            {}
        )

        if not categorias:

            await interaction.response.send_message(
                "❌ No hay categorías configuradas.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="✦ 𝐑𝐎𝐋𝐄𝐒 𝐃𝐄𝐋 𝐒𝐄𝐑𝐕𝐈𝐃𝐎𝐑 ✦",
            description=(
                "**Elegí tus roles utilizando "
                "los menús de abajo.**\n\n"
                "🟣 Podés cambiar tus roles "
                "cuando quieras."
            ),
            color=discord.Color.from_rgb(
                145,
                70,
                255
            )
        )

        embed.set_footer(
            text=(
                f"{interaction.guild.name} "
                "• Sistema de roles"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

        canal = interaction.channel

        if canal is None:
            return

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

            try:

                view = RoleView(
                    categoria,
                    titulo,
                    opciones,
                    interaction.guild
                )

            except Exception as error:

                print(
                    f"❌ [ROLES] "
                    f"{categoria}: {error}"
                )

                continue

            texto = (
                f"**{titulo}**"
            )

            if descripcion:

                texto += (
                    f"\n{descripcion}"
                )

            try:

                message = await canal.send(
                    texto,
                    view=view
                )

                # Registrar la view asociada
                # al mensaje.
                self.bot.add_view(
                    view,
                    message_id=message.id
                )

                print(
                    f"✅ [ROLES] Panel enviado: "
                    f"{categoria}"
                )

            except Exception as error:

                print(
                    f"❌ [ROLES] Error enviando "
                    f"{categoria}: {error}"
                )

    # ========================================================
    # /CREAR_ROLES
    # ========================================================

    @app_commands.command(
        name="crear_roles",
        description="Comprueba los roles configurados."
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
                "❌ Este comando solo funciona en servidores.",
                ephemeral=True
            )

            return

        data = cargar_roles()

        guild_data = data.get(
            str(interaction.guild.id),
            {}
        )

        categorias = guild_data.get(
            "categorias",
            {}
        )

        encontrados = 0
        faltantes = 0

        for config in categorias.values():

            for role_id in config.get(
                "roles",
                {}
            ).values():

                if obtener_rol(
                    interaction.guild,
                    role_id
                ):

                    encontrados += 1

                else:

                    faltantes += 1

        await interaction.response.send_message(
            (
                "🔎 **Comprobación de roles**\n\n"
                f"✅ Encontrados: `{encontrados}`\n"
                f"❌ Faltantes: `{faltantes}`"
            ),
            ephemeral=True
        )

    # ========================================================
    # ERROR
    # ========================================================

    @roles.error
    async def roles_error(
        self,
        interaction,
        error
    ):

        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):

            mensaje = (
                "❌ Necesitás **Gestionar roles**."
            )

        else:

            print(
                f"[ROLES] Error /roles: {error}"
            )

            mensaje = (
                "❌ Ocurrió un error ejecutando /roles."
            )

        try:

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

        except Exception:
            pass


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        ReactionRoles(bot)
    )