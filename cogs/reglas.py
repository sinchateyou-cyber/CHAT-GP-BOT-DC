import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# ARCHIVOS
# ============================================================
DATA_FOLDER = "data"
RULES_FILE = "data/reglas.json"
VERIFICATION_FILE = "data/verification.json"
# ============================================================
# FUNCIONES
# ============================================================
def ensure_data_folder():
    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )
def load_json(
    filename
):
    ensure_data_folder()
    if not os.path.exists(
        filename
    ):
        return {}
    try:
        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(
                file
            )
            if isinstance(
                data,
                dict
            ):
                return data
    except (
        json.JSONDecodeError,
        OSError
    ):
        pass
    return {}
def save_json(
    filename,
    data
):
    ensure_data_folder()
    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )
def load_rules():
    return load_json(
        RULES_FILE
    )
def save_rules(
    data
):
    save_json(
        RULES_FILE,
        data
    )
# ============================================================
# VIEW DE REGLAS
# ============================================================
class ReglasView(
    discord.ui.View
):
    def __init__(
        self
    ):
        super().__init__(
            timeout=None
        )
    @discord.ui.button(
        label="Aceptar reglas",
        emoji="✅",
        style=discord.ButtonStyle.success,
        custom_id="reglas_aceptar_definitivo"
    )
    async def aceptar(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este botón solo funciona dentro de un servidor.",
                ephemeral=True
            )
            return
        guild_id = str(
            interaction.guild.id
        )
        user_id = str(
            interaction.user.id
        )
        data = load_rules()
        if guild_id not in data:
            data[guild_id] = {
                "accepted": {}
            }
        if "accepted" not in data[guild_id]:
            data[guild_id]["accepted"] = {}
        # ====================================================
        # COMPROBAR SI YA ACEPTÓ
        # ====================================================
        if user_id in data[guild_id]["accepted"]:
            await interaction.response.send_message(
                "✅ Ya aceptaste las reglas de este servidor.",
                ephemeral=True
            )
            return
        # ====================================================
        # GUARDAR ACEPTACIÓN
        # ====================================================
        data[guild_id]["accepted"][user_id] = {
            "username":
                str(
                    interaction.user
                ),
            "display_name":
                interaction.user.display_name,
            "timestamp":
                discord.utils.utcnow().isoformat()
        }
        save_rules(
            data
        )
        # ====================================================
        # BUSCAR ROL VERIFICADO
        # ====================================================
        role = discord.utils.get(
            interaction.guild.roles,
            name="Verificado"
        )
        if role:
            member = interaction.guild.get_member(
                interaction.user.id
            )
            if member and role not in member.roles:
                try:
                    await member.add_roles(
                        role,
                        reason="Aceptó las reglas del servidor."
                    )
                except discord.Forbidden:
                    await interaction.response.send_message(
                        "⚠️ Aceptaste las reglas y quedaste registrado, "
                        "pero no pude asignarte el rol `Verificado`.\n\n"
                        "El administrador debe revisar los permisos "
                        "y la posición del rol del bot.",
                        ephemeral=True
                    )
                    return
        # ====================================================
        # RESPUESTA
        # ====================================================
        await interaction.response.send_message(
            "✅ **Reglas aceptadas correctamente.**\n"
            "🎉 Ya estás verificado y podés acceder al servidor.",
            ephemeral=True
        )
# ============================================================
# COG REGLAS
# ============================================================
class Reglas(
    commands.Cog
):
    def __init__(
        self,
        bot
    ):
        self.bot = bot
        ensure_data_folder()
        # Registrar botón persistente
        self.bot.add_view(
            ReglasView()
        )
    # ========================================================
    # /reglas
    # ========================================================
    @app_commands.command(
        name="reglas",
        description="Muestra las reglas del servidor."
    )
    @app_commands.guild_only()
    async def reglas(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="📜 Reglas del servidor",
            description=(
                "**1. Respeto**\n"
                "Respetá a todos los miembros del servidor.\n\n"
                "**2. No spam**\n"
                "No hagas spam, flood ni menciones masivas.\n\n"
                "**3. No contenido malicioso**\n"
                "Está prohibido compartir contenido ilegal, "
                "malicioso o peligroso.\n\n"
                "**4. No publicidad**\n"
                "No hagas publicidad sin autorización del staff.\n\n"
                "**5. Usá los canales correctamente**\n"
                "Publicá cada contenido en el canal correspondiente.\n\n"
                "**6. Respetá al staff**\n"
                "Seguí las indicaciones del equipo de moderación.\n\n"
                "**7. Aceptación**\n"
                "Al presionar **Aceptar reglas**, confirmás que "
                "leíste y aceptás las reglas del servidor."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Presioná el botón para aceptar las reglas."
        )
        await interaction.response.send_message(
            embed=embed,
            view=ReglasView()
        )
    # ========================================================
    # /reglas-aceptadas
    # ========================================================
    @app_commands.command(
        name="reglas-aceptadas",
        description="Muestra quiénes aceptaron las reglas."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(
        manage_guild=True
    )
    async def reglas_aceptadas(
        self,
        interaction: discord.Interaction
    ):
        data = load_rules()
        guild_id = str(
            interaction.guild.id
        )
        guild_data = data.get(
            guild_id,
            {}
        )
        accepted = guild_data.get(
            "accepted",
            {}
        )
        if not accepted:
            await interaction.response.send_message(
                "📋 Nadie aceptó las reglas todavía.",
                ephemeral=True
            )
            return
        lines = []
        for user_id, info in accepted.items():
            member = interaction.guild.get_member(
                int(
                    user_id
                )
            )
            if member:
                name = member.mention
            else:
                name = (
                    info.get(
                        "display_name",
                        info.get(
                            "username",
                            f"Usuario {user_id}"
                        )
                    )
                )
            lines.append(
                f"• {name}"
            )
        description = "\n".join(
            lines[:50]
        )
        if len(accepted) > 50:
            description += (
                f"\n\n... y "
                f"{len(accepted) - 50} usuarios más."
            )
        embed = discord.Embed(
            title="📋 Usuarios que aceptaron las reglas",
            description=description,
            color=discord.Color.green()
        )
        embed.add_field(
            name="👥 Total",
            value=str(
                len(
                    accepted
                )
            ),
            inline=False
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )
# ============================================================
# SETUP
# ============================================================
async def setup(
    bot
):
    await bot.add_cog(
        Reglas(
            bot
        )
    )