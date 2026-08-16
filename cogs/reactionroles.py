import discord
from discord.ext import commands
from discord import app_commands

import json
import os
import traceback


# ============================================================
# CONFIGURACIÓN
# ============================================================

ROLES_FILE = "data/roles.json"


# ============================================================
# CARGAR ROLES
# ============================================================

def cargar_roles():

    try:

        if not os.path.exists(ROLES_FILE):

            print(
                f"❌ No existe {ROLES_FILE}"
            )

            return {}

        with open(
            ROLES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if not isinstance(data, dict):

            print(
                "❌ roles.json no contiene un objeto válido."
            )

            return {}

        return data

    except json.JSONDecodeError as e:

        print(
            f"❌ roles.json tiene JSON inválido: {e}"
        )

        return {}

    except Exception as e:

        print(
            f"❌ Error leyendo roles.json: {e}"
        )

        traceback.print_exc()

        return {}


# ============================================================
# OBTENER ROL
# ============================================================

def obtener_rol(
    guild,
    role_id
):

    try:

        return guild.get_role(
            int(role_id)
        )

    except Exception:

        return None


# ============================================================
# ROLE SELECT
# ============================================================

class RoleSelect(
    discord.ui.Select
):

    def __init__(
        self,
        guild,
        categoria,
        titulo,
        opciones
    ):

        self.guild_id = guild.id
        self.categoria = str(categoria)

        options = []

        # ----------------------------------------------------
        # CREAR OPCIONES
        # ----------------------------------------------------

        for emoji, role_id in opciones.items():

            role = obtener_rol(
                guild,
                role_id
            )

            if role is None:

                print(
                    f"⚠️ Rol {role_id} no existe "
                    f"en {guild.name}"
                )

                continue

            # No permitir roles administrados
            if role.managed:

                print(
                    f"⚠️ Rol administrado ignorado: "
                    f"{role.name}"
                )

                continue

            try:

                options.append(
                    discord.SelectOption(
                        label=role.name[:100],
                        value=str(role.id),
                        emoji=emoji
                    )
                )

            except Exception as e:

                print(
                    f"⚠️ Error creando opción "
                    f"{role_id}: {e}"
                )

        # ----------------------------------------------------
        # SIN ROLES
        # ----------------------------------------------------

        if not options:

            raise ValueError(
                f"No hay roles válidos para "
                f"{categoria}"
            )

        # ----------------------------------------------------
        # CUSTOM ID PERSISTENTE
        # ----------------------------------------------------

        custom_id = (
            f"reactionrole:"
            f"{guild.id}:"
            f"{self.categoria}"
        )

        super().__init__(
            placeholder=(
                f"Seleccioná {titulo}"[:150]
            ),
            min_values=1,
            max_values=1,
            options=options,
            custom_id=custom_id
        )

    # ========================================================
    # CALLBACK
    # ========================================================

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        try:

            # ------------------------------------------------
            # COMPROBAR SERVIDOR
            # ------------------------------------------------

            if interaction.guild is None:

                await interaction.response.send_message(
                    "❌ Este menú solo funciona "
                    "dentro de un servidor.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # OBTENER ROL
            # ------------------------------------------------

            try:

                role_id = int(
                    self.values[0]
                )

            except (ValueError, IndexError):

                await interaction.response.send_message(
                    "❌ Selección de rol inválida.",
                    ephemeral=True
                )

                return

            role = interaction.guild.get_role(
                role_id
            )

            if role is None:

                await interaction.response.send_message(
                    "❌ No encontré ese rol.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # MIEMBRO
            # ------------------------------------------------

            member = interaction.user

            if not isinstance(
                member,
                discord.Member
            ):

                member = await interaction.guild.fetch_member(
                    interaction.user.id
                )

            # ------------------------------------------------
            # BOT MEMBER
            # ------------------------------------------------

            bot_member = interaction.guild.me

            if bot_member is None:

                try:

                    bot_member = (
                        await interaction.guild.fetch_member(
                            interaction.client.user.id
                        )
                    )

                except Exception:

                    bot_member = None

            if bot_member is None:

                await interaction.response.send_message(
                    "❌ No pude comprobar los permisos "
                    "del bot.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # PERMISOS
            # ------------------------------------------------

            if not bot_member.guild_permissions.manage_roles:

                await interaction.response.send_message(
                    "❌ El bot no tiene "
                    "**Gestionar roles**.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # ROL ADMINISTRADO
            # ------------------------------------------------

            if role.managed:

                await interaction.response.send_message(
                    "❌ Ese rol es administrado por Discord "
                    "y no puede asignarse.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # JERARQUÍA
            # ------------------------------------------------

            if role >= bot_member.top_role:

                await interaction.response.send_message(
                    "❌ No puedo asignarte ese rol.\n\n"
                    f"El rol del bot debe estar por encima "
                    f"de {role.mention}.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # CARGAR CONFIGURACIÓN
            # ------------------------------------------------

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

            roles_config = categoria_data.get(
                "roles",
                {}
            )

            if not roles_config:

                await interaction.response.send_message(
                    "❌ Esta categoría no está "
                    "configurada correctamente.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # COMPROBAR QUE EL ROL PERTENECE A LA CATEGORÍA
            # ------------------------------------------------

            roles_categoria = set()

            for configured_role_id in roles_config.values():

                try:

                    roles_categoria.add(
                        int(configured_role_id)
                    )

                except Exception:

                    continue

            if role.id not in roles_categoria:

                await interaction.response.send_message(
                    "❌ Ese rol no pertenece a "
                    "esta categoría.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # QUITAR OTROS ROLES DE LA CATEGORÍA
            # ------------------------------------------------

            quitar = []

            for other_role_id in roles_config.values():

                other_role = obtener_rol(
                    interaction.guild,
                    other_role_id
                )

                if other_role is None:
                    continue

                if other_role.id == role.id:
                    continue

                if other_role in member.roles:

                    quitar.append(
                        other_role
                    )

            if quitar:

                try:

                    await member.remove_roles(
                        *quitar,
                        reason=(
                            f"Reaction Role - "
                            f"{self.categoria}"
                        )
                    )

                except discord.Forbidden:

                    await interaction.response.send_message(
                        "❌ No pude quitar tus roles "
                        "anteriores.",
                        ephemeral=True
                    )

                    return

            # ------------------------------------------------
            # YA TIENE EL ROL
            # ------------------------------------------------

            if role in member.roles:

                await interaction.response.send_message(
                    f"ℹ️ Ya tenés {role.mention}.",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # DAR ROL
            # ------------------------------------------------

            try:

                await member.add_roles(
                    role,
                    reason=(
                        f"Reaction Role - "
                        f"{self.categoria}"
                    )
                )

            except discord.Forbidden:

                await interaction.response.send_message(
                    "❌ Discord rechazó la operación.\n\n"
                    "Revisá:\n"
                    "• Gestionar roles\n"
                    "• Posición del rol del bot\n"
                    "• Que el rol no sea administrado",
                    ephemeral=True
                )

                return

            # ------------------------------------------------
            # RESPUESTA
            # ------------------------------------------------

            await interaction.response.send_message(
                f"✅ Te asigné {role.mention}.",
                ephemeral=True
            )

            print(
                f"🎭 {member} recibió "
                f"{role.name} "
                f"en {interaction.guild.name} "
                f"[{self.categoria}]"
            )

        except discord.NotFound:

            try:

                await interaction.response.send_message(
                    "❌ La interacción expiró. "
                    "Volvé a seleccionar el rol.",
                    ephemeral=True
                )

            except Exception:

                pass

        except discord.Forbidden:

            try:

                if interaction.response.is_done():

                    await interaction.followup.send(
                        "❌ Discord rechazó la operación.",
                        ephemeral=True
                    )

                else:

                    await interaction.response.send_message(
                        "❌ Discord rechazó la operación.",
                        ephemeral=True
                    )

            except Exception:

                pass

        except Exception as e:

            print(
                f"❌ ERROR REACTION ROLE: {e}"
            )

            traceback.print_exc()

            try:

                if interaction.response.is_done():

                    await interaction.followup.send(
                        "❌ Ocurrió un error.",
                        ephemeral=True
                    )

                else:

                    await interaction.response.send_message(
                        "❌ Ocurrió un error.",
                        ephemeral=True
                    )

            except Exception:

                pass


# ============================================================
# VIEW PERSISTENTE
# ============================================================

class RoleView(
    discord.ui.View
):

    def __init__(
        self,
        guild,
        categoria,
        titulo,
        opciones
    ):

        super().__init__(
            timeout=None
        )

        self.add_item(
            RoleSelect(
                guild,
                categoria,
                titulo,
                opciones
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
            "🎭 Reaction Roles cargado."
        )

    # ========================================================
    # REGISTRAR VIEWS PERSISTENTES
    # ========================================================

    async def registrar_views_persistentes(
        self
    ):

        data = cargar_roles()

        if not data:

            print(
                "⚠️ No hay configuraciones "
                "en roles.json."
            )

            return

        registradas = 0

        # ----------------------------------------------------
        # RECORRER SERVIDORES
        # ----------------------------------------------------

        for guild_id, guild_data in data.items():

            try:

                guild = self.bot.get_guild(
                    int(guild_id)
                )

            except Exception:

                continue

            if guild is None:

                print(
                    f"⚠️ Servidor {guild_id} "
                    f"no está disponible."
                )

                continue

            categorias = guild_data.get(
                "categorias",
                {}
            )

            # ------------------------------------------------
            # RECORRER CATEGORÍAS
            # ------------------------------------------------

            for categoria, config in categorias.items():

                try:

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

                    view = RoleView(
                        guild,
                        categoria,
                        titulo,
                        opciones
                    )

                    self.bot.add_view(
                        view
                    )

                    registradas += 1

                    print(
                        f"♻️ View persistente registrada: "
                        f"{guild.name} / "
                        f"{categoria}"
                    )

                except ValueError as e:

                    print(
                        f"⚠️ No se pudo registrar "
                        f"{categoria}: {e}"
                    )

                except Exception as e:

                    print(
                        f"❌ Error registrando "
                        f"{categoria}: {e}"
                    )

                    traceback.print_exc()

        print(
            f"♻️ Views persistentes registradas: "
            f"{registradas}"
        )

    # ========================================================
    # /ROLES
    # ========================================================

    @app_commands.command(
        name="roles",
        description="Envía los paneles de roles."
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
                "❌ Usá este comando dentro "
                "de un servidor.",
                ephemeral=True
            )

            return

        print(
            f"🎭 /roles ejecutado por "
            f"{interaction.user} "
            f"en {interaction.guild.name}"
        )

        data = cargar_roles()

        guild_data = data.get(
            str(interaction.guild.id)
        )

        if guild_data is None:

            await interaction.response.send_message(
                "❌ Este servidor no está configurado "
                "en `data/roles.json`.",
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

        await interaction.response.send_message(
            "✅ Paneles de roles enviados.",
            ephemeral=True
        )

        enviados = 0

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
                    interaction.guild,
                    categoria,
                    titulo,
                    opciones
                )

                texto = titulo

                if descripcion:

                    texto += (
                        f"\n{descripcion}"
                    )

                await interaction.channel.send(
                    texto,
                    view=view
                )

                enviados += 1

                print(
                    f"✅ Panel enviado: "
                    f"{categoria}"
                )

            except Exception as e:

                print(
                    f"❌ Error enviando "
                    f"{categoria}: {e}"
                )

                traceback.print_exc()

        print(
            f"🎭 Total paneles enviados: "
            f"{enviados}"
        )

    # ========================================================
    # /CREAR_ROLES
    # ========================================================

    @app_commands.command(
        name="crear_roles",
        description="Comprueba los roles del panel."
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
                "❌ Usá este comando dentro "
                "de un servidor.",
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

        for categoria, config in categorias.items():

            for emoji, role_id in config.get(
                "roles",
                {}
            ).items():

                role = obtener_rol(
                    interaction.guild,
                    role_id
                )

                if role:

                    encontrados += 1

                else:

                    faltantes += 1

                    print(
                        f"❌ Falta {role_id} "
                        f"({categoria} / {emoji})"
                    )

        await interaction.response.send_message(
            "🔎 **REVISIÓN DE REACTION ROLES**\n\n"
            f"✅ Roles encontrados: `{encontrados}`\n"
            f"❌ Roles faltantes: `{faltantes}`",
            ephemeral=True
        )

    # ========================================================
    # ERROR /ROLES
    # ========================================================

    @roles.error
    async def roles_error(
        self,
        interaction,
        error
    ):

        print(
            f"❌ Error /roles: {error}"
        )

        try:

            if isinstance(
                error,
                app_commands.errors.MissingPermissions
            ):

                mensaje = (
                    "❌ Necesitás "
                    "**Gestionar roles**."
                )

            else:

                mensaje = (
                    "❌ Hubo un error ejecutando "
                    "`/roles`."
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

        except Exception:

            pass


# ============================================================
# SETUP
# ============================================================

async def setup(
    bot
):

    cog = ReactionRoles(
        bot
    )

    await bot.add_cog(
        cog
    )

    print(
        "♻️ Registrando Reaction Roles persistentes..."
    )

    await cog.registrar_views_persistentes()

    print(
        "✅ cogs.reactionroles listo."
    )