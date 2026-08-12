import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import traceback

ROLES_FILE = "data/roles.json"


# ============================================================
# ROLES JSON
# ============================================================

def cargar_roles():
    if not os.path.exists(ROLES_FILE):
        return {}

    try:
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception as e:
        print(f"[REACTION ROLES] Error leyendo roles.json: {e}")
        return {}


def obtener_rol(guild, role_id):
    try:
        return guild.get_role(int(role_id))
    except (TypeError, ValueError):
        return None


# ============================================================
# CUSTOM ID
# ============================================================

def custom_id(guild_id, categoria):
    return f"rr_{guild_id}_{categoria}"


# ============================================================
# PROCESAR SELECCIÓN
# ============================================================

async def procesar_rol(interaction, categoria, opciones):

    if interaction.guild is None:
        await interaction.response.send_message(
            "❌ Este menú solamente funciona dentro de un servidor.",
            ephemeral=True
        )
        return

    if not interaction.values:
        await interaction.response.send_message(
            "❌ No seleccionaste ningún rol.",
            ephemeral=True
        )
        return

    role_id = interaction.values[0]

    rol = obtener_rol(
        interaction.guild,
        role_id
    )

    if rol is None:
        await interaction.response.send_message(
            "❌ Ese rol no existe o fue eliminado.",
            ephemeral=True
        )
        return

    # ========================================================
    # BOT
    # ========================================================

    bot_member = interaction.guild.me

    if bot_member is None:
        try:
            bot_member = await interaction.guild.fetch_member(
                interaction.client.user.id
            )
        except Exception as e:
            print(f"[REACTION ROLES] No pude obtener al bot: {e}")

            await interaction.response.send_message(
                "❌ No pude comprobar los permisos del bot.",
                ephemeral=True
            )
            return

    # ========================================================
    # COMPROBAR JERARQUÍA
    # ========================================================

    if rol.managed:
        await interaction.response.send_message(
            "❌ Ese rol es administrado por una integración y no se puede asignar.",
            ephemeral=True
        )
        return

    if rol >= bot_member.top_role:
        await interaction.response.send_message(
            "❌ **No puedo darte ese rol.**\n\n"
            "El rol del bot tiene que estar **por encima** "
            "del rol que querés seleccionar.",
            ephemeral=True
        )
        return

    # ========================================================
    # COMPROBAR PERMISO
    # ========================================================

    if not bot_member.guild_permissions.manage_roles:
        await interaction.response.send_message(
            "❌ El bot no tiene el permiso **Gestionar roles**.",
            ephemeral=True
        )
        return

    # ========================================================
    # ROLES DE LA MISMA CATEGORÍA
    # ========================================================

    quitar = []

    for otro_id in opciones.values():

        otro_rol = obtener_rol(
            interaction.guild,
            otro_id
        )

        if otro_rol is None:
            continue

        if otro_rol.id == rol.id:
            continue

        if otro_rol in interaction.user.roles:
            quitar.append(otro_rol)

    # ========================================================
    # ASIGNAR
    # ========================================================

    try:

        if quitar:
            await interaction.user.remove_roles(
                *quitar,
                reason=f"Reaction Roles - {categoria}"
            )

        if rol not in interaction.user.roles:

            await interaction.user.add_roles(
                rol,
                reason=f"Reaction Roles - {categoria}"
            )

            await interaction.response.send_message(
                f"✅ Te asigné {rol.mention}.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                f"ℹ️ Ya tenés {rol.mention}.",
                ephemeral=True
            )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Discord rechazó el cambio de rol.\n\n"
            "Revisá que el bot tenga **Gestionar roles** "
            "y que su rol esté por encima del rol seleccionado.",
            ephemeral=True
        )

    except discord.HTTPException as e:

        print(
            f"[REACTION ROLES] HTTP ERROR: {e}"
        )

        await interaction.response.send_message(
            "❌ Discord devolvió un error al modificar el rol.",
            ephemeral=True
        )

    except Exception as e:

        print(
            f"[REACTION ROLES] ERROR: {e}"
        )

        traceback.print_exc()

        await interaction.response.send_message(
            "❌ Ocurrió un error al asignar el rol.",
            ephemeral=True
        )


# ============================================================
# SELECT
# ============================================================

class RoleSelect(discord.ui.Select):

    def __init__(
        self,
        guild,
        categoria,
        titulo,
        opciones
    ):

        self.categoria = categoria

        opciones_discord = []

        for emoji, role_id in opciones.items():

            rol = obtener_rol(
                guild,
                role_id
            )

            if rol is None:
                print(
                    f"[REACTION ROLES] "
                    f"Rol inexistente: {role_id}"
                )
                continue

            if rol.managed:
                continue

            if len(opciones_discord) >= 25:
                break

            opciones_discord.append(
                discord.SelectOption(
                    label=rol.name[:100],
                    value=str(rol.id),
                    emoji=emoji
                )
            )

        if not opciones_discord:
            raise ValueError(
                f"No hay roles válidos en {categoria}"
            )

        super().__init__(
            placeholder=f"Seleccioná {titulo}...",
            min_values=1,
            max_values=1,
            options=opciones_discord,
            custom_id=custom_id(
                guild.id,
                categoria
            )
        )

    async def callback(self, interaction):

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

        await procesar_rol(
            interaction,
            self.categoria,
            opciones
        )


# ============================================================
# VIEW
# ============================================================

class RoleView(discord.ui.View):

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

class ReactionRoles(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        print(
            "🎭 [REACTION ROLES] Cog cargado."
        )

    # ========================================================
    # REGISTRAR TODAS LAS VIEWS
    # ========================================================

    async def registrar_views(self):

        print("")
        print("=" * 60)
        print("🎭 REGISTRANDO REACTION ROLES")
        print("=" * 60)

        data = cargar_roles()

        if not data:
            print("⚠️ roles.json está vacío.")
            return

        total = 0

        for guild_id, guild_data in data.items():

            try:
                guild = self.bot.get_guild(
                    int(guild_id)
                )
            except Exception:
                guild = None

            if guild is None:
                print(
                    f"⚠️ Servidor no encontrado: {guild_id}"
                )
                continue

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
                        guild,
                        categoria,
                        titulo,
                        opciones
                    )

                    self.bot.add_view(
                        view
                    )

                    total += 1

                    print(
                        f"✅ {guild.name} → {categoria}"
                    )

                except Exception as e:

                    print(
                        f"❌ Error {categoria}: {e}"
                    )

        print(
            f"🎭 Views registradas: {total}"
        )

        print("=" * 60)

    # ========================================================
    # /ROLES
    # ========================================================

    @app_commands.command(
        name="roles",
        description="Envía el panel de roles."
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
                "❌ Usá este comando dentro del servidor.",
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

        await interaction.response.send_message(
            "✅ Panel de roles enviado.",
            ephemeral=True
        )

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

            try:

                view = RoleView(
                    interaction.guild,
                    categoria,
                    titulo,
                    opciones
                )

            except Exception as e:

                print(
                    f"❌ No se pudo crear "
                    f"{categoria}: {e}"
                )

                continue

            texto = f"**{titulo}**"

            if descripcion:
                texto += f"\n{descripcion}"

            try:

                await canal.send(
                    texto,
                    view=view
                )

                print(
                    f"✅ Panel enviado: {categoria}"
                )

            except Exception as e:

                print(
                    f"❌ Error enviando "
                    f"{categoria}: {e}"
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
            "🔎 **Reaction Roles**\n\n"
            f"✅ Roles encontrados: `{encontrados}`\n"
            f"❌ Roles faltantes: `{faltantes}`",
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
                f"[REACTION ROLES] Error: {error}"
            )

            mensaje = (
                "❌ Hubo un error con `/roles`."
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

    cog = ReactionRoles(bot)

    await bot.add_cog(cog)

    # IMPORTANTE:
    # Esperamos a que Discord tenga los servidores cargados.
    if bot.is_ready():
        await cog.registrar_views()
    else:
        async def registrar_despues():
            await bot.wait_until_ready()
            await cog.registrar_views()

        bot.loop.create_task(
            registrar_despues()
        )