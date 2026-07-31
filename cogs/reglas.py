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
# ============================================================
# FUNCIONES
# ============================================================
def ensure_data_folder():
    os.makedirs(
        DATA_FOLDER,
        exist_ok=True
    )
def load_data():
    ensure_data_folder()
    if not os.path.exists(
        RULES_FILE
    ):
        data = {}
        save_data(
            data
        )
        return data
    try:
        with open(
            RULES_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(
                file
            )
            if not isinstance(
                data,
                dict
            ):
                return {}
            return data
    except (
        json.JSONDecodeError,
        OSError
    ):
        return {}
def save_data(
    data
):
    ensure_data_folder()
    with open(
        RULES_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
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
        custom_id="reglas_aceptar"
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
        data = load_data()
        if guild_id not in data:
            data[guild_id] = {
                "channel_id":
                    interaction.channel.id,
                "message_id":
                    interaction.message.id,
                "accepted":
                    {}
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
        save_data(
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
            try:
                member = interaction.guild.get_member(
                    interaction.user.id
                )
                if member and role not in member.roles:
                    await member.add_roles(
                        role,
                        reason="Aceptó las reglas del servidor."
                    )
            except discord.Forbidden:
                await interaction.response.send_message(
                    "✅ Reglas aceptadas y guardadas.\n"
                    "⚠️ No pude asignarte el rol `Verificado`. "
                    "Revisá la posición y permisos del rol del bot.",
                    ephemeral=True
                )
                return
        # ====================================================
        # RESPUESTA
        # ====================================================
        await interaction.response.send_message(
            "✅ **Reglas aceptadas correctamente.**\n"
            "Ya quedaste registrado como miembro verificado.",
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
                "**1.** Respetá a todos los miembros.\n\n"
                "**2.** No se permite spam ni flood.\n\n"
                "**3.** No compartas contenido ilegal o malicioso.\n\n"
                "**4.** No hagas publicidad sin permiso del staff.\n\n"
                "**5.** Usá los canales correctamente.\n\n"
                "**6.** Seguí las indicaciones del equipo de moderación.\n\n"
                "**7.** Al presionar el botón **Aceptar reglas**, "
                "confirmás que leíste y aceptás las reglas del servidor."
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Aceptá las reglas para continuar."
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
        data = load_data()
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
                "📋 Todavía nadie aceptó las reglas.",
                ephemeral=True
            )
            return
        # ====================================================
        # CREAR LISTA
        # ====================================================
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
            timestamp = info.get(
                "timestamp",
                "Fecha desconocida"
            )
            lines.append(
                f"• {name} — `{timestamp}`"
            )
        # ====================================================
        # EMBED
        # ====================================================
        embed = discord.Embed(
            title="📋 Usuarios que aceptaron las reglas",
            description="\n".join(
                lines[:50]
            ),
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
        embed.set_footer(
            text=f"Servidor ID: {interaction.guild.id}"
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