import json
import os
import traceback

import discord
from discord import app_commands
from discord.ext import commands


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLES_FILE = "data/roles.json"


# ============================================================
# CARGAR ROLES
# ============================================================

def cargar_roles():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(ROLES_FILE):
        return {}

    try:
        with open(
            ROLES_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, dict):
            return {}

        return data

    except json.JSONDecodeError as error:
        print(
            f"[REACTION ROLES] ❌ JSON inválido: {error}"
        )
        return {}

    except OSError as error:
        print(
            f"[REACTION ROLES] ❌ Error leyendo roles.json: {error}"
        )
        return {}


# ============================================================
# GUARDAR ROLES
# ============================================================

def guardar_roles(data):

    os.makedirs("data", exist_ok=True)

    try:

        with open(
            ROLES_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        return True

    except OSError as error:

        print(
            f"[REACTION ROLES] ❌ Error guardando roles: {error}"
        )

        return False


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

def crear_custom_id(
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

    # --------------------------------------------------------
    # COMPROBAR SERVIDOR
    # --------------------------------------------------------

    if interaction.guild is None:

        if not interaction.response.is_done():

            await interaction.response.send_message(
                "❌ Este menú solamente puede utilizarse "
                "dentro de un servidor.",
                ephemeral=True
            )

        return

    # --------------------------------------------------------
    # COMPROBAR SELECCIÓN
    # --------------------------------------------------------

    if not interaction.values:

        if not interaction.response.is_done():

            await interaction.response.send_message(
                "❌ No se pudo obtener el rol seleccionado.",
                ephemeral=True
            )

        return

    # --------------------------------------------------------
    # ID SELECCIONADO
    # --------------------------------------------------------

    selected_id = interaction.values[0]

    selected_role = obtener_rol(
        interaction.guild,
        selected_id
    )

    if selected_role is None:

        await interaction.response.send_message(
            "❌ Ese rol ya no existe en el servidor.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # OBTENER BOT
    # --------------------------------------------------------

    me = interaction.guild.me

    if me is None:

        try:

            if interaction.client.user is None:

                await interaction.response.send_message(
                    "❌ No pude identificar al bot.",
                    ephemeral=True
                )

                return

            me = await interaction.guild.fetch_member(
                interaction.client.user.id
            )

        except Exception as error:

            print(
                "[REACTION ROLES] "
                f"❌ Error obteniendo miembro del bot: {error}"
            )

            await interaction.response.send_message(
                "❌ No pude obtener la información del bot.",
                ephemeral=True
            )

            return

    # --------------------------------------------------------
    # COMPROBAR PERMISOS
    # --------------------------------------------------------

    if not me.guild_permissions.manage_roles:

        await interaction.response.send_message(
            "❌ No tengo el permiso **Gestionar roles**.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # COMPROBAR JERARQUÍA
    # --------------------------------------------------------

    if selected_role.managed:

        await interaction.response.send_message(
            "❌ Ese rol es administrado por Discord "
            "y no puede asignarse manualmente.",
            ephemeral=True
        )

        return

    if selected_role >= me.top_role:

        await interaction.response.send_message(
            "❌ No puedo asignar ese rol porque está por encima "
            "o al mismo nivel que mi rol más alto.\n\n"
            "📌 Mové el rol del bot por encima de los roles "
            "de Reaction Roles.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # ROLES DE LA MISMA CATEGORÍA
    # --------------------------------------------------------

    roles_to_remove = []

    for role_id in opciones.values():

        role = obtener_rol(
            interaction.guild,
            role_id
        )

        if role is None:
            continue

        if role.id == selected_role.id:
            continue

        if role in interaction.user.roles:

            roles_to_remove.append(
                role
            )

    # --------------------------------------------------------
    # COMPROBAR SI YA LO TIENE
    # --------------------------------------------------------

    already_has_role = (
        selected_role in interaction.user.roles
    )

    try:

        # ----------------------------------------------------
        # QUITAR OTROS ROLES DE LA CATEGORÍA
        # ----------------------------------------------------

        if roles_to_remove:

            await interaction.user.remove_roles(
                *roles_to_remove,
                reason=(
                    "Reaction Roles - "
                    f"cambio de categoría {categoria}"
                )
            )

        # ----------------------------------------------------
        # SI YA LO TENÍA
        # ----------------------------------------------------

        if already_has_role:

            # No lo quitamos.
            # El sistema funciona como selector de categoría.

            mensaje = (
                "ℹ️ Ya tenés seleccionado "
                f"{selected_role.mention}."
            )

        # ----------------------------------------------------
        # ASIGNAR ROL
        # ----------------------------------------------------

        else:

            await interaction.user.add_roles(
                selected_role,
                reason=(
                    "Reaction Roles - "
                    f"{categoria}"
                )
            )

            mensaje = (
                "✅ **Rol asignado correctamente.**\n\n"
                f"🎭 {selected_role.mention}"
            )

        # ----------------------------------------------------
        # RESPONDER
        # ----------------------------------------------------

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

    # --------------------------------------------------------
    # SIN PERMISOS
    # --------------------------------------------------------

    except discord.Forbidden:

        print(
            "[REACTION ROLES] ❌ Discord rechazó "
            "la modificación del rol."
        )

        try:

            if interaction.response.is_done():

                await interaction.followup.send(
                    (
                        "❌ No tengo permisos suficientes "
                        "para modificar ese rol."
                    ),
                    ephemeral=True
                )

            else:

                await interaction.response.send_message(
                    (
                        "❌ No tengo permisos suficientes "
                        "para modificar ese rol.\n\n"
                        "Asegurate de que el rol del bot esté "
                        "por encima de los roles configurados."
                    ),
                    ephemeral=True
                )

        except Exception:
            pass

    # --------------------------------------------------------
    # ERROR HTTP
    # --------------------------------------------------------

    except discord.HTTPException as error:

        print(
            "[REACTION ROLES] "
            f"❌ HTTPException: {error}"
        )

        try:

            if interaction.response.is_done():

                await interaction.followup.send(
                    "❌ Discord rechazó la modificación del rol.",
                    ephemeral=True
                )

            else:

                await interaction.response.send_message(
                    "❌ Discord rechazó la modificación del rol.",
                    ephemeral=True
                )

        except Exception:
            pass

    # --------------------------------------------------------
    # ERROR GENERAL
    # --------------------------------------------------------

    except Exception as error:

        print(
            "[REACTION ROLES] "
            f"❌ Error inesperado: {error}"
        )

        traceback.print_exc()

        try:

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

        except Exception:
            pass


# ============================================================
# SELECT
# ============================================================

class RoleSelect(discord.ui.Select):

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

            # -----------------------------------------------
            # ROL INEXISTENTE
            # -----------------------------------------------

            if role is None:

                print(
                    "[REACTION ROLES] "
                    f"⚠️ Rol inexistente: {role_id}"
                )

                continue

            # -----------------------------------------------
            # MÁXIMO DISCORD
            # -----------------------------------------------

            if len(select_options) >= 25:
                break

            # -----------------------------------------------
            # OPCIÓN
            # -----------------------------------------------

            try:

                option = discord.SelectOption(
                    label=role.name[:100],
                    emoji=emoji,
                    value=str(role.id),
                    description=(
                        f"Seleccionar {role.name[:90]}"
                    )
                )

                select_options.append(
                    option
                )

            except Exception as error:

                print(
                    "[REACTION ROLES] "
                    f"⚠️ Error creando opción {role_id}: "
                    f"{error}"
                )

        # ----------------------------------------------------
        # SIN OPCIONES
        # ----------------------------------------------------

        if not select_options:

            raise ValueError(
                f"La categoría '{categoria}' "
                "no tiene roles válidos."
            )

        # ----------------------------------------------------
        # SELECT
        # ----------------------------------------------------

        super().__init__(
            placeholder=(
                f"Seleccioná "
                f"{titulo.replace('*', '').lower()}..."
            ),
            min_values=1,
            max_values=1,
            options=select_options,
            custom_id=crear_custom_id(
                self.guild_id,
                categoria
            )
        )

    # ========================================================
    # CALLBACK
    # ========================================================

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        print(
            "[REACTION ROLES] "
            f"🟣 Selección recibida: "
            f"{self.categoria} "
            f"por {interaction.user} "
            f"({interaction.user.id})"
        )

        try:

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
                    (
                        "❌ Esta categoría ya no tiene "
                        "roles configurados."
                    ),
                    ephemeral=True
                )

                return

            await procesar_rol(
                interaction=interaction,
                categoria=self.categoria,
                opciones=opciones
            )

        except Exception as error:

            print(
                "[REACTION ROLES] "
                f"❌ Error en callback: {error}"
            )

            traceback.print_exc()

            try:

                if interaction.response.is_done():

                    await interaction.followup.send(
                        "❌ Ocurrió un error con el menú de roles.",
                        ephemeral=True
                    )

                else:

                    await interaction.response.send_message(
                        "❌ Ocurrió un error con el menú de roles.",
                        ephemeral=True
                    )

            except Exception:
                pass


# ============================================================
# VIEW
# ============================================================

class RoleView(discord.ui.View):

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

        self.categoria = categoria
        self.guild_id = guild.id

        self.add_item(
            RoleSelect(
                categoria=categoria,
                titulo=titulo,
                opciones=opciones,
                guild=guild
            )
        )


# ============================================================
# COG
# ============================================================

class ReactionRoles(commands.Cog):

    def __init__(
        self,
        bot
    ):

        self.bot = bot

        print(
            "[REACTION ROLES] "
            "✅ Sistema cargado."
        )

        # IMPORTANTE:
        # NO registramos views acá.
        #
        # El bot.py las registra después de cargar
        # todos los Cogs y cuando el Guild ya está disponible.

    # ========================================================
    # /ROLES
    # ========================================================

    @app_commands.command(
        name="roles",
        description="Muestra el panel para elegir tus roles."
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
                (
                    "❌ Este comando solamente puede "
                    "utilizarse dentro de un servidor."
                ),
                ephemeral=True
            )

            return

        data = cargar_roles()

        guild_id = str(
            interaction.guild.id
        )

        guild_data = data.get(
            guild_id
        )

        if not guild_data:

            await interaction.response.send_message(
                (
                    "❌ Este servidor todavía no tiene "
                    "roles configurados."
                ),
                ephemeral=True
            )

            return

        categorias = guild_data.get(
            "categorias",
            {}
        )

        if not categorias:

            await interaction.response.send_message(
                (
                    "❌ No hay categorías de roles "
                    "configuradas."
                ),
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="✦ 𝐑𝐎𝐋𝐄𝐒 𝐃𝐄𝐋 𝐒𝐄𝐑𝐕𝐈𝐃𝐎𝐑 ✦",
            description=(
                "**Elegí tus roles utilizando "
                "los menús de abajo.**\n"
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
            text=(
                f"{interaction.guild.name} "
                "• Sistema de roles"
            )
        )

        # ----------------------------------------------------
        # RESPONDER PRIMERO
        # ----------------------------------------------------

        await interaction.response.send_message(
            embed=embed
        )

        # ----------------------------------------------------
        # CANAL
        # ----------------------------------------------------

        canal = interaction.channel

        if canal is None:
            return

        # ----------------------------------------------------
        # CREAR PANELES
        # ----------------------------------------------------

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

            # ------------------------------------------------
            # VALIDAR ROLES
            # ------------------------------------------------

            opciones_validas = {}

            for emoji, role_id in opciones.items():

                role = obtener_rol(
                    interaction.guild,
                    role_id
                )

                if role is None:

                    print(
                        "[REACTION ROLES] "
                        f"⚠️ {categoria}: "
                        f"rol inexistente {role_id}"
                    )

                    continue

                opciones_validas[emoji] = str(
                    role.id
                )

            if not opciones_validas:

                print(
                    "[REACTION ROLES] "
                    f"⚠️ {categoria}: "
                    "sin roles válidos."
                )

                continue

            # ------------------------------------------------
            # CREAR VIEW
            # ------------------------------------------------

            try:

                view = RoleView(
                    categoria=categoria,
                    titulo=titulo,
                    opciones=opciones_validas,
                    guild=interaction.guild
                )

            except Exception as error:

                print(
                    "[REACTION ROLES] "
                    f"❌ Error creando view {categoria}: "
                    f"{error}"
                )

                traceback.print_exc()

                continue

            # ------------------------------------------------
            # TEXTO
            # ------------------------------------------------

            contenido = (
                f"**{titulo}**"
            )

            if descripcion:

                contenido += (
                    f"\n{descripcion}"
                )

            # ------------------------------------------------
            # ENVIAR
            # ------------------------------------------------

            try:

                message = await canal.send(
                    content=contenido,
                    view=view
                )

                print(
                    "[REACTION ROLES] "
                    f"✅ Panel creado: "
                    f"{categoria} "
                    f"| mensaje {message.id}"
                )

                # Registrar view con message_id
                # para persistencia.

                try:

                    self.bot.add_view(
                        view,
                        message_id=message.id
                    )

                except Exception as error:

                    print(
                        "[REACTION ROLES] "
                        f"⚠️ No se pudo registrar "
                        f"message_id: {error}"
                    )

            except discord.HTTPException as error:

                print(
                    "[REACTION ROLES] "
                    f"❌ Error enviando "
                    f"{categoria}: {error}"
                )

            except Exception as error:

                print(
                    "[REACTION ROLES] "
                    f"❌ Error inesperado enviando "
                    f"{categoria}: {error}"
                )

    # ========================================================
    # /CREAR_ROLES
    # ========================================================

    @app_commands.command(
        name="crear_roles",
        description="Comprueba los roles configurados por ID."
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
                (
                    "❌ Este comando solamente funciona "
                    "en un servidor."
                ),
                ephemeral=True
            )

            return

        data = cargar_roles()

        guild_id = str(
            interaction.guild.id
        )

        guild_data = data.get(
            guild_id
        )

        if not guild_data:

            await interaction.response.send_message(
                (
                    "❌ No hay configuración para "
                    "este servidor."
                ),
                ephemeral=True
            )

            return

        categorias = guild_data.get(
            "categorias",
            {}
        )

        encontrados = 0
        faltantes = 0

        detalles = []

        for categoria, config in categorias.items():

            roles = config.get(
                "roles",
                {}
            )

            for emoji, role_id in roles.items():

                role = obtener_rol(
                    interaction.guild,
                    role_id
                )

                if role:

                    encontrados += 1

                    detalles.append(
                        f"✅ {emoji} → {role.mention}"
                    )

                else:

                    faltantes += 1

                    detalles.append(
                        f"❌ {emoji} → `{role_id}`"
                    )

        # ----------------------------------------------------
        # EMBED
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🔎 Comprobación de Reaction Roles",
            description=(
                f"**Roles encontrados:** `{encontrados}`\n"
                f"**Roles faltantes:** `{faltantes}`"
            ),
            color=(
                discord.Color.green()
                if faltantes == 0
                else discord.Color.orange()
            )
        )

        # Discord tiene límite de descripción.
        # Mostramos solamente una parte.

        if detalles:

            texto = "\n".join(
                detalles
            )

            embed.add_field(
                name="Roles",
                value=texto[:1024],
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    # ========================================================
    # ERROR /ROLES
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

            mensaje = (
                "❌ Necesitás **Gestionar roles** "
                "para usar este comando."
            )

        else:

            print(
                "[REACTION ROLES] "
                f"❌ Error /roles: {error}"
            )

            traceback.print_exc()

            mensaje = (
                "❌ Ocurrió un error al ejecutar "
                "`/roles`."
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

    # ========================================================
    # ERROR /CREAR_ROLES
    # ========================================================

    @crear_roles.error
    async def crear_roles_error(
        self,
        interaction: discord.Interaction,
        error
    ):

        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):

            mensaje = (
                "❌ Necesitás **Gestionar roles** "
                "para usar este comando."
            )

        else:

            print(
                "[REACTION ROLES] "
                f"❌ Error /crear_roles: {error}"
            )

            traceback.print_exc()

            mensaje = (
                "❌ Ocurrió un error al comprobar "
                "los roles."
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

    print(
        "[REACTION ROLES] "
        "✅ Cog instalado correctamente."
    )