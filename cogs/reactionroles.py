import discord
from discord.ext import commands
from discord import app_commands
import json
import os


ROLES_FILE = "data/roles.json"


# ============================================================
# CARGAR ROLES
# ============================================================

def cargar_roles():
    if not os.path.exists(ROLES_FILE):
        return {}

    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data if isinstance(data, dict) else {}

    except (json.JSONDecodeError, OSError) as e:
        print(f"[REACTION ROLES] Error leyendo roles.json: {e}")
        return {}


# ============================================================
# GUARDAR ROLES
# ============================================================

def guardar_roles(data):
    os.makedirs("data", exist_ok=True)

    try:
        with open(ROLES_FILE, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    except OSError as e:
        print(f"[REACTION ROLES] Error guardando roles.json: {e}")


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
# CUSTOM ID
# ============================================================

def crear_custom_id(guild_id, categoria):
    return f"reactionroles:{guild_id}:{categoria}"


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
            "❌ Este menú solamente puede utilizarse dentro de un servidor.",
            ephemeral=True
        )
        return

    if not interaction.values:

        await interaction.response.send_message(
            "❌ No se pudo obtener el rol seleccionado.",
            ephemeral=True
        )
        return

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

    # ========================================================
    # BOT
    # ========================================================

    me = interaction.guild.me

    if me is None:

        try:

            if interaction.client.user:

                me = await interaction.guild.fetch_member(
                    interaction.client.user.id
                )

        except Exception as e:

            print(
                f"[REACTION ROLES] Error obteniendo bot: {e}"
            )

    if me is None:

        await interaction.response.send_message(
            "❌ No pude obtener la información del bot.",
            ephemeral=True
        )
        return

    # ========================================================
    # COMPROBAR JERARQUÍA
    # ========================================================

    if selected_role.is_default():

        await interaction.response.send_message(
            "❌ No podés seleccionar el rol @everyone.",
            ephemeral=True
        )
        return

    if selected_role.managed:

        await interaction.response.send_message(
            "❌ Ese rol está administrado por una integración y no se puede asignar.",
            ephemeral=True
        )
        return

    if selected_role >= me.top_role:

        await interaction.response.send_message(
            "❌ No puedo asignar ese rol porque está por encima "
            "o al mismo nivel que mi rol más alto.\n\n"
            "Subí el rol del bot por encima de los roles de reacción.",
            ephemeral=True
        )
        return

    # ========================================================
    # COMPROBAR PERMISOS
    # ========================================================

    if not me.guild_permissions.manage_roles:

        await interaction.response.send_message(
            "❌ El bot no tiene el permiso **Gestionar roles**.",
            ephemeral=True
        )
        return

    # ========================================================
    # ROLES DE LA MISMA CATEGORÍA
    # ========================================================

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

    # ========================================================
    # MODIFICAR ROLES
    # ========================================================

    try:

        if roles_to_remove:

            await interaction.user.remove_roles(
                *roles_to_remove,
                reason=f"Reaction Roles - cambio en {categoria}"
            )

        # ----------------------------------------------------
        # SI YA LO TIENE
        # ----------------------------------------------------

        if selected_role in interaction.user.roles:

            mensaje = (
                "ℹ️ Ya tenés asignado "
                f"{selected_role.mention}."
            )

        # ----------------------------------------------------
        # ASIGNAR
        # ----------------------------------------------------

        else:

            await interaction.user.add_roles(
                selected_role,
                reason=f"Reaction Roles - {categoria}"
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

    except discord.Forbidden:

        print(
            "[REACTION ROLES] Discord Forbidden al modificar roles."
        )

        if not interaction.response.is_done():

            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para modificar ese rol.\n\n"
                "Asegurate de que:\n"
                "• El bot tenga **Gestionar roles**.\n"
                "• El rol del bot esté por encima de los roles configurados.",
                ephemeral=True
            )

        return

    except discord.HTTPException as e:

        print(
            f"[REACTION ROLES] Error HTTP: {e}"
        )

        if not interaction.response.is_done():

            await interaction.response.send_message(
                "❌ Discord rechazó la modificación del rol. "
                "Probá nuevamente.",
                ephemeral=True
            )

        return

    except Exception as e:

        print(
            f"[REACTION ROLES] Error inesperado: {e}"
        )

        if not interaction.response.is_done():

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
        guild=None,
        guild_id=None
    ):

        self.categoria = categoria

        # ----------------------------------------------------
        # OBTENER GUILD ID
        # ----------------------------------------------------

        if guild is not None:

            self.guild_id = guild.id

        elif guild_id is not None:

            self.guild_id = int(guild_id)

        else:

            raise ValueError(
                "RoleSelect necesita guild o guild_id."
            )

        select_options = []

        # ====================================================
        # CREAR OPCIONES
        # ====================================================

        for emoji, role_id in opciones.items():

            try:

                role_id_int = int(role_id)

            except (TypeError, ValueError):

                continue

            # ------------------------------------------------
            # SI TENEMOS GUILD, USAR NOMBRE DEL ROL
            # ------------------------------------------------

            role_name = f"Rol {role_id_int}"

            if guild is not None:

                role = guild.get_role(
                    role_id_int
                )

                if role is None:
                    continue

                role_name = role.name

            # ------------------------------------------------
            # MÁXIMO 25 OPCIONES
            # ------------------------------------------------

            if len(select_options) >= 25:
                break

            try:

                option = discord.SelectOption(
                    label=role_name[:100],
                    emoji=emoji,
                    value=str(role_id_int)
                )

            except Exception:

                option = discord.SelectOption(
                    label=role_name[:100],
                    value=str(role_id_int)
                )

            select_options.append(
                option
            )

        # ====================================================
        # VALIDAR
        # ====================================================

        if not select_options:

            raise ValueError(
                f"La categoría '{categoria}' "
                "no tiene roles válidos."
            )

        # ====================================================
        # SELECT
        # ====================================================

        super().__init__(
            placeholder=f"Seleccioná {titulo.lower()}...",
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

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ Este menú solamente funciona dentro de un servidor.",
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
        guild=None,
        guild_id=None
    ):

        super().__init__(
            timeout=None
        )

        self.categoria = categoria

        # ----------------------------------------------------
        # OBTENER GUILD ID
        # ----------------------------------------------------

        if guild is not None:

            self.guild_id = guild.id

        elif guild_id is not None:

            self.guild_id = int(guild_id)

        else:

            raise ValueError(
                "RoleView necesita guild o guild_id."
            )

        # ----------------------------------------------------
        # SELECT
        # ----------------------------------------------------

        self.add_item(
            RoleSelect(
                categoria=categoria,
                titulo=titulo,
                opciones=opciones,
                guild=guild,
                guild_id=self.guild_id
            )
        )


# ============================================================
# COG
# ============================================================

class ReactionRoles(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print(
            "[REACTION ROLES] Sistema cargado."
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

        # ====================================================
        # EMBED
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
                        f"[REACTION ROLES] "
                        f"Rol inexistente: {role_id}"
                    )

                    continue

                opciones_validas[emoji] = str(
                    role.id
                )

            if not opciones_validas:

                print(
                    f"[REACTION ROLES] "
                    f"{categoria}: no hay roles válidos."
                )

                continue

            # ------------------------------------------------
            # VIEW
            # ------------------------------------------------

            try:

                view = RoleView(
                    categoria=categoria,
                    titulo=titulo,
                    opciones=opciones_validas,
                    guild=interaction.guild
                )

            except Exception as e:

                print(
                    f"[REACTION ROLES] "
                    f"Error creando {categoria}: {e}"
                )

                continue

            # ------------------------------------------------
            # CONTENIDO
            # ------------------------------------------------

            contenido = f"**{titulo}**"

            if descripcion:

                contenido += (
                    f"\n{descripcion}"
                )

            # ------------------------------------------------
            # ENVIAR
            # ------------------------------------------------

            try:

                message = await canal.send(
                    contenido,
                    view=view
                )

                # ------------------------------------------------
                # REGISTRAR VIEW CON MESSAGE ID
                # ------------------------------------------------

                self.bot.add_view(
                    view,
                    message_id=message.id
                )

                print(
                    f"[REACTION ROLES] "
                    f"Panel creado: "
                    f"{categoria} "
                    f"| mensaje={message.id}"
                )

            except discord.HTTPException as e:

                print(
                    f"[REACTION ROLES] "
                    f"Error enviando {categoria}: {e}"
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
                "❌ Este comando solamente funciona "
                "en un servidor.",
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

        await interaction.response.send_message(
            (
                "🔎 **Comprobación de Reaction Roles**\n\n"
                f"✅ Roles encontrados: `{encontrados}`\n"
                f"❌ Roles faltantes: `{faltantes}`"
            ),
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
                "[REACTION ROLES] Error /roles:"
            )

            traceback_text = (
                f"{type(error).__name__}: {error}"
            )

            print(
                traceback_text
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