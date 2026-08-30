import json
from pathlib import Path

import discord
from discord.ext import commands
from discord import app_commands


DATA_FOLDER = Path("data")
DATA_FILE = DATA_FOLDER / "reaction_roles.json"


# ============================================================
# DATOS
# ============================================================

def cargar_datos():
    DATA_FOLDER.mkdir(exist_ok=True)

    if not DATA_FILE.exists():
        DATA_FILE.write_text("{}", encoding="utf-8")

    try:
        data = json.loads(
            DATA_FILE.read_text(encoding="utf-8")
        )

        if isinstance(data, dict):
            return data

        return {}

    except Exception as e:
        print(f"❌ Error leyendo reaction_roles.json: {e}")
        return {}


def guardar_datos(data):
    DATA_FOLDER.mkdir(exist_ok=True)

    try:
        DATA_FILE.write_text(
            json.dumps(
                data,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

    except Exception as e:
        print(f"❌ Error guardando reaction_roles.json: {e}")


# ============================================================
# BOTÓN PERSISTENTE
# ============================================================

class RoleButton(discord.ui.Button):

    def __init__(self, role_id: int):

        self.role_id = role_id

        super().__init__(
            label="Obtener rol",
            emoji="💜",
            style=discord.ButtonStyle.primary,

            # IMPORTANTE:
            # custom_id fijo para que Discord pueda reconocer
            # el botón después de reiniciar el bot.
            custom_id=f"reaction_role:{role_id}"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ====================================================
        # BUSCAR ROL
        # ====================================================

        role = interaction.guild.get_role(
            self.role_id
        )

        if role is None:
            return await interaction.response.send_message(
                "❌ No encontré el rol configurado.",
                ephemeral=True
            )

        # ====================================================
        # COMPROBAR PERMISOS
        # ====================================================

        me = interaction.guild.me

        if me is None:
            return await interaction.response.send_message(
                "❌ No pude comprobar los permisos del bot.",
                ephemeral=True
            )

        if me.top_role <= role:
            return await interaction.response.send_message(
                "❌ No puedo administrar ese rol porque está "
                "por encima de mi rol más alto.",
                ephemeral=True
            )

        # ====================================================
        # DAR / QUITAR ROL
        # ====================================================

        try:

            if role in interaction.user.roles:

                await interaction.user.remove_roles(
                    role,
                    reason="Reaction Role - quitar rol"
                )

                await interaction.response.send_message(
                    f"❌ Te saqué el rol {role.mention}.",
                    ephemeral=True
                )

            else:

                await interaction.user.add_roles(
                    role,
                    reason="Reaction Role - obtener rol"
                )

                await interaction.response.send_message(
                    f"✅ Te asigné el rol {role.mention}.",
                    ephemeral=True
                )

        except discord.Forbidden:

            await interaction.response.send_message(
                "❌ No tengo permisos para administrar ese rol.",
                ephemeral=True
            )

        except Exception as e:

            print(
                f"❌ Error administrando rol "
                f"{self.role_id}: {e}"
            )

            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al administrar el rol.",
                    ephemeral=True
                )


# ============================================================
# VIEW PERSISTENTE
# ============================================================

class RoleView(discord.ui.View):

    def __init__(self, role_id: int):

        # IMPORTANTE:
        # timeout=None = View persistente.
        super().__init__(timeout=None)

        self.add_item(
            RoleButton(role_id)
        )


# ============================================================
# COG
# ============================================================

class ReactionRoles(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.data = cargar_datos()

    # ========================================================
    # CARGAR PANELES AL INICIAR
    # ========================================================

    async def cog_load(self):

        cargados = 0

        for guild_id, panel in self.data.items():

            try:

                role_id = int(
                    panel["role_id"]
                )

                # Registrar View persistente
                self.bot.add_view(
                    RoleView(role_id)
                )

                cargados += 1

                print(
                    f"✅ Panel de roles cargado "
                    f"(guild: {guild_id}, role: {role_id})"
                )

            except KeyError:
                print(
                    f"⚠️ Panel {guild_id} no tiene role_id."
                )

            except ValueError:
                print(
                    f"⚠️ role_id inválido en panel {guild_id}."
                )

            except Exception as e:
                print(
                    f"❌ Error cargando panel "
                    f"{guild_id}: {e}"
                )

        print(
            f"✅ {cargados} panel(es) de roles cargado(s)."
        )

    # ========================================================
    # /rolpanel
    # ========================================================

    @app_commands.command(
        name="rolpanel",
        description="Crea un panel para obtener un rol mediante un botón."
    )
    @app_commands.describe(
        rol="El rol que se entregará al tocar el botón.",
        titulo="Título del panel.",
        descripcion="Descripción del panel."
    )
    @app_commands.default_permissions(
        manage_roles=True
    )
    async def rolpanel(
        self,
        interaction: discord.Interaction,
        rol: discord.Role,
        titulo: str = "💜 Obtener rol",
        descripcion: str = "Tocá el botón para obtener este rol."
    ):

        # ====================================================
        # SERVIDOR
        # ====================================================

        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # ====================================================
        # PERMISOS
        # ====================================================

        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message(
                "❌ Necesitás el permiso **Gestionar roles**.",
                ephemeral=True
            )

        # ====================================================
        # JERARQUÍA
        # ====================================================

        me = interaction.guild.me

        if me is None:
            return await interaction.response.send_message(
                "❌ No pude comprobar la jerarquía del bot.",
                ephemeral=True
            )

        if me.top_role <= rol:
            return await interaction.response.send_message(
                "❌ No puedo asignar ese rol porque está "
                "por encima de mi rol más alto.",
                ephemeral=True
            )

        # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title=titulo,
            description=(
                f"{descripcion}\n\n"
                f"🎭 **Rol:** {rol.mention}\n\n"
                "**Tocá el botón de abajo para obtenerlo.**"
            ),
            color=discord.Color.from_rgb(
                128,
                0,
                255
            )
        )

        embed.set_footer(
            text=interaction.guild.name
        )

        # ====================================================
        # VIEW PERSISTENTE
        # ====================================================

        view = RoleView(
            rol.id
        )

        # ====================================================
        # ENVIAR PANEL
        # ====================================================

        try:

            mensaje = await interaction.channel.send(
                embed=embed,
                view=view
            )

        except discord.Forbidden:

            return await interaction.response.send_message(
                "❌ No tengo permisos para enviar mensajes "
                "o usar componentes en este canal.",
                ephemeral=True
            )

        except Exception as e:

            print(
                f"❌ Error enviando panel: {e}"
            )

            return await interaction.response.send_message(
                "❌ No pude crear el panel.",
                ephemeral=True
            )

        # ====================================================
        # GUARDAR PANEL
        # ====================================================

        guild_id = str(
            interaction.guild.id
        )

        self.data[guild_id] = {
            "role_id": rol.id,
            "channel_id": interaction.channel.id,
            "message_id": mensaje.id
        }

        guardar_datos(
            self.data
        )

        # ====================================================
        # RESPUESTA
        # ====================================================

        await interaction.response.send_message(
            "✅ Panel de roles creado correctamente.\n"
            "💾 También quedó guardado para que siga "
            "funcionando después de reiniciar el bot.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):

    await bot.add_cog(
        ReactionRoles(bot)
    )