import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLES_FILE = "data/roles.json"


# ============================================================
# CARGAR ROLES
# ============================================================

def cargar_roles():
    if not os.path.exists(ROLES_FILE):
        return {}

    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except (json.JSONDecodeError, OSError):
        return {}


# ============================================================
# GUARDAR ROLES
# ============================================================

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
# OBTENER ROL
# ============================================================

def obtener_rol(guild: discord.Guild, role_id):

    try:
        role_id = int(role_id)
    except (TypeError, ValueError):
        return None

    return guild.get_role(role_id)


# ============================================================
# CREAR ID DEL SELECT
# ============================================================

def crear_custom_id(guild_id, categoria):

    return f"reactionroles:{guild_id}:{categoria}"


# ============================================================
# PROCESAR SELECCIÓN DE ROL
# ============================================================

async def procesar_rol(
    interaction: discord.Interaction,
    categoria: str,
    opciones: dict
):

    if interaction.guild is None:

        await interaction.response.send_message(
            "❌ Este menú solamente puede utilizarse dentro de un servidor.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # COMPROBAR QUE HAYA UNA SELECCIÓN
    # --------------------------------------------------------

    if not interaction.data:

        await interaction.response.send_message(
            "❌ No se pudo obtener la selección.",
            ephemeral=True
        )

        return

    try:
        selected_id = interaction.data.get("values", [None])[0]
    except Exception:
        selected_id = None

    if selected_id is None:

        await interaction.response.send_message(
            "❌ No se pudo obtener el rol seleccionado.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # ROL SELECCIONADO
    # --------------------------------------------------------

    selected_role = obtener_rol(
        interaction.guild,
        selected_id
    )

    if selected_role is None:

        await interaction.response.send_message(
            f"❌ El rol `{selected_id}` ya no existe en el servidor.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # BOT
    # --------------------------------------------------------

    me = interaction.guild.me

    if me is None:

        try:
            me = await interaction.guild.fetch_member(
                interaction.client.user.id
            )
        except Exception:

            await interaction.response.send_message(
                "❌ No pude obtener los permisos del bot.",
                ephemeral=True
            )

            return

    # --------------------------------------------------------
    # JERARQUÍA
    # --------------------------------------------------------

    if selected_role >= me.top_role:

        await interaction.response.send_message(
            "❌ No puedo asignar ese rol porque está por encima "
            "o al mismo nivel que mi rol más alto.",
            ephemeral=True
        )

        return

    # --------------------------------------------------------
    # BUSCAR ROLES DE LA MISMA CATEGORÍA
    # --------------------------------------------------------

    roles_to_remove = []

    for role_id in opciones.values():

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

    # --------------------------------------------------------
    # MODIFICAR ROLES
    # --------------------------------------------------------

    try:

        # Quitar otros roles de la categoría
        if roles_to_remove:

            await interaction.user.remove_roles(
                *roles_to_remove,
                reason=f"Reaction Roles - cambio en {categoria}"
            )

        # Agregar seleccionado
        if selected_role not in interaction.user.roles:

            await interaction.user.add_roles(
                selected_role,
                reason=f"Reaction Roles - {categoria}"
            )

            mensaje = (
                "✅ **Rol asignado correctamente.**\n\n"
                f"🎭 {selected_role.mention}"
            )

        else:

            mensaje = (
                "ℹ️ Ya tenés asignado "
                f"{selected_role.mention}."
            )

        await interaction.response.send_message(
            mensaje,
            ephemeral=True
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ No tengo permisos suficientes para modificar ese rol.\n\n"
            "Asegurate de que mi rol esté **por encima** de los roles "
            "que quiero asignar.",
            ephemeral=True
        )

    except discord.HTTPException as e:

        print(
            f"[REACTION ROLES] Error HTTP en {categoria}: {e}"
        )

        await interaction.response.send_message(
            "❌ Discord rechazó la modificación del rol. "
            "Probá nuevamente.",
            ephemeral=True
        )

    except Exception as e:

        print(
            f"[REACTION ROLES] Error inesperado en {categoria}: {e}"
        )

        await interaction.response.send_message(
            "❌ Ocurrió un error inesperado al modificar el rol.",
            ephemeral=True
        )


# ============================================================
# SELECT PERSISTENTE
# ============================================================

class RoleSelect(discord.ui.Select):

    def __init__(
        self,
        categoria,
        titulo,
        opciones,
        guild_id
    ):

        self.categoria = categoria
        self.guild_id = guild_id

        select_options = []

        for emoji, role_id in opciones.items():

            role_id_int = None

            try:
                role_id_int = int(role_id)
            except (TypeError, ValueError):
                continue

            # ------------------------------------------------
            # Discord permite máximo 25 opciones
            # ------------------------------------------------

            if len(select_options) >= 25:
                break

            select_options.append(
                discord.SelectOption(
                    label=f"Rol {role_id_int}",
                    emoji=emoji,
                    value=str(role_id_int)
                )
            )

        if not select_options:

            raise ValueError(
                f"La categoría '{categoria}' no tiene roles válidos."
            )

        super().__init__(
            placeholder=f"Seleccioná {titulo.lower()}...",
            min_values=1,
            max_values=1,
            options=select_options,
            custom_id=crear_custom_id(
                guild_id,
                categoria
            )
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        # ----------------------------------------------------
        # RECARGAR JSON
        # ----------------------------------------------------

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
                "❌ Esta categoría ya no tiene roles configurados.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # PROCESAR
        # ----------------------------------------------------

        await procesar_rol(
            interaction,
            self.categoria,
            opciones
        )


# ============================================================
# VIEW PERSISTENTE
# ============================================================

class RoleView(discord.ui.View):

    def __init__(
        self,
        categoria,
        titulo,
        opciones,
        guild_id
    ):

        super().__init__(
            timeout=None
        )

        self.add_item(
            RoleSelect(
                categoria,
                titulo,
                opciones,
                guild_id
            )
        )


# ============================================================
# COG
# ============================================================

class ReactionRoles(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        # ----------------------------------------------------
        # Registrar las Views existentes
        # ----------------------------------------------------

        self.registrar_views()

    # ========================================================
    # REGISTRAR VIEWS
    # ========================================================

    def registrar_views(self):

        data = cargar_roles()

        cantidad = 0

        for guild_id, guild_data in data.items():

            categorias = guild_data.get(
                "categorias",
                {}
            )

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
                        guild_id
                    )

                    self.bot.add_view(
                        view
                    )

                    cantidad += 1

                except Exception as e:

                    print(
                        f"[REACTION ROLES] "
                        f"No se pudo registrar "
                        f"{guild_id}/{categoria}: {e}"
                    )

        print(
            f"[REACTION ROLES] "
            f"Views persistentes registradas: {cantidad}"
        )

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
                "❌ Este comando solamente puede utilizarse "
                "dentro de un servidor.",
                ephemeral=True
            )

            return

        data = cargar_roles()

        guild_id = str(
            interaction.guild.id
        )

        if guild_id not in data:

            await interaction.response.send_message(
                "❌ Este servidor todavía no tiene roles configurados.",
                ephemeral=True
            )

            return

        categorias = data[guild_id].get(
            "categorias",
            {}
        )

        if not categorias:

            await interaction.response.send_message(
                "❌ No hay categorías de roles configuradas.",
                ephemeral=True
            )

            return

        # ----------------------------------------------------
        # MENSAJE PRINCIPAL
        # ----------------------------------------------------

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
            text=(
                f"{interaction.guild.name} "
                "• Sistema de roles"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )

        # ----------------------------------------------------
        # CREAR PANELES
        # ----------------------------------------------------

        canal = interaction.channel

        if canal is None:
            return

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

            # -----------------------------------------------
            # FILTRAR ROLES EXISTENTES
            # -----------------------------------------------

            opciones_validas = {}

            for emoji, role_id in opciones.items():

                role = obtener_rol(
                    interaction.guild,
                    role_id
                )

                if role is None:
                    print(
                        f"[REACTION ROLES] "
                        f"Rol inexistente: {role_id}"
                    )
                    continue

                opciones_validas[emoji] = str(
                    role.id
                )

            if not opciones_validas:
                continue

            # -----------------------------------------------
            # CREAR VIEW PERSISTENTE
            # -----------------------------------------------

            try:

                view = RoleView(
                    categoria,
                    titulo,
                    opciones_validas,
                    guild_id
                )

            except ValueError as e:

                print(
                    f"[REACTION ROLES] {e}"
                )

                continue

            # -----------------------------------------------
            # TEXTO
            # -----------------------------------------------

            contenido = f"**{titulo}**"

            if descripcion:

                contenido += (
                    f"\n{descripcion}"
                )

            # -----------------------------------------------
            # ENVIAR
            # -----------------------------------------------

            try:

                message = await canal.send(
                    contenido,
                    view=view
                )

                # -------------------------------------------
                # REGISTRAR VIEW
                # -------------------------------------------

                self.bot.add_view(
                    view,
                    message_id=message.id
                )

                print(
                    f"[REACTION ROLES] "
                    f"Panel creado: "
                    f"{categoria} "
                    f"({message.id})"
                )

            except discord.HTTPException as e:

                print(
                    f"[REACTION ROLES] "
                    f"Error enviando panel "
                    f"{categoria}: {e}"
                )

                continue

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

        encontrados = 0
        faltantes = 0

        for config in categorias.values():

            roles = config.get(
                "roles",
                {}
            )

            for role_id in roles.values():

                role = obtener_rol(
                    interaction.guild,
                    role_id
                )

                if role:
                    encontrados += 1
                else:
                    faltantes += 1

        mensaje = (
            "🔎 **Comprobación de Reaction Roles**\n\n"
            f"✅ Roles encontrados: `{encontrados}`\n"
            f"❌ Roles faltantes: `{faltantes}`"
        )

        await interaction.response.send_message(
            mensaje,
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
                f"[REACTION ROLES] Error /roles: {error}"
            )

            mensaje = (
                "❌ Ocurrió un error al ejecutar `/roles`."
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