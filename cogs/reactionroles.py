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
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def guardar_datos(data):
    DATA_FOLDER.mkdir(exist_ok=True)
    DATA_FILE.write_text(
        json.dumps(data, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )


# ============================================================
# BOTÓN
# ============================================================

class RoleButton(discord.ui.Button):
    def __init__(self, role_id: int):
        super().__init__(
            label="Obtener rol",
            emoji="💜",
            style=discord.ButtonStyle.primary,
            custom_id=f"reaction_role:{role_id}"
        )

        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):

        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )

        role = interaction.guild.get_role(self.role_id)

        if role is None:
            return await interaction.response.send_message(
                "❌ No encontré el rol configurado.",
                ephemeral=True
            )

        # Comprobar permisos del bot
        if interaction.guild.me.top_role <= role:
            return await interaction.response.send_message(
                "❌ No puedo asignar ese rol porque está por encima de mi rol más alto.",
                ephemeral=True
            )

        try:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)

                await interaction.response.send_message(
                    f"❌ Te saqué el rol {role.mention}.",
                    ephemeral=True
                )

            else:
                await interaction.user.add_roles(role)

                await interaction.response.send_message(
                    f"✅ Te asigné el rol {role.mention}.",
                    ephemeral=True
                )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para administrar ese rol.",
                ephemeral=True
            )

        except Exception:
            await interaction.response.send_message(
                "❌ Ocurrió un error al administrar el rol.",
                ephemeral=True
            )


# ============================================================
# VIEW
# ============================================================

class RoleView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.add_item(RoleButton(role_id))


# ============================================================
# COG
# ============================================================

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = cargar_datos()

    # --------------------------------------------------------
    # CARGAR BOTONES AL REINICIAR
    # --------------------------------------------------------

    async def cog_load(self):

        for guild_id, panel in self.data.items():

            try:
                role_id = int(panel["role_id"])
                self.bot.add_view(RoleView(role_id))

            except Exception as e:
                print(f"❌ Error cargando panel {guild_id}: {e}")

        print("✅ Paneles de roles cargados.")

    # --------------------------------------------------------
    # CREAR PANEL
    # --------------------------------------------------------

    @app_commands.command(
        name="rolpanel",
        description="Crea un panel para obtener un rol mediante un botón."
    )
    @app_commands.describe(
        rol="El rol que se entregará al tocar el botón.",
        titulo="Título del panel.",
        descripcion="Descripción del panel."
    )
    @app_commands.default_permissions(manage_roles=True)
    async def rolpanel(
        self,
        interaction: discord.Interaction,
        rol: discord.Role,
        titulo: str = "💜 Obtener rol",
        descripcion: str = "Tocá el botón para obtener este rol."
    ):

        if interaction.guild is None:
            return await interaction.response.send_message(
                "❌ Este comando solo funciona dentro de un servidor.",
                ephemeral=True
            )

        # Comprobar jerarquía
        if interaction.guild.me.top_role <= rol:
            return await interaction.response.send_message(
                "❌ No puedo asignar ese rol porque está por encima de mi rol más alto.",
                ephemeral=True
            )

        embed = discord.Embed(
            title=titulo,
            description=(
                f"{descripcion}\n\n"
                f"🎭 **Rol:** {rol.mention}\n\n"
                "**Tocá el botón de abajo para obtenerlo.**"
            ),
            color=discord.Color.from_rgb(128, 0, 255)
        )

        embed.set_footer(
            text=f"{interaction.guild.name}"
        )

        view = RoleView(rol.id)

        await interaction.channel.send(
            embed=embed,
            view=view
        )

        # Guardar panel
        guild_id = str(interaction.guild.id)

        self.data[guild_id] = {
            "role_id": rol.id
        }

        guardar_datos(self.data)

        await interaction.response.send_message(
            "✅ Panel de roles creado correctamente.",
            ephemeral=True
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))