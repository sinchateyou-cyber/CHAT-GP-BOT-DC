import os
import json
import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# CONFIGURACIÓN
# ============================================================
DATA_FOLDER = "data"
DATA_FILE = "data/xp.json"
# ============================================================
# CARGAR DATOS
# ============================================================
def load_data():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    if not os.path.exists(DATA_FILE):
        with open(
            DATA_FILE,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                {},
                file,
                indent=4
            )
    try:
        with open(
            DATA_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            return json.load(file)
    except Exception:
        return {}
# ============================================================
# GUARDAR DATOS
# ============================================================
def save_data(data):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    with open(
        DATA_FILE,
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
# XP NECESARIA PARA EL SIGUIENTE NIVEL
# ============================================================
def xp_required(level):
    return 100 + (
        level * 50
    )
# ============================================================
# CALCULAR NIVEL
# ============================================================
def calculate_level(total_xp):
    level = 0
    remaining_xp = total_xp
    while remaining_xp >= xp_required(level):
        remaining_xp -= xp_required(level)
        level += 1
    return level, remaining_xp
# ============================================================
# COG ADD XP
# ============================================================
class AddXP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ========================================================
    # /ADDXP
    # ========================================================
    @app_commands.command(
        name="addxp",
        description="Agrega XP a un usuario."
    )
    @app_commands.describe(
    usuario="Usuario al que querés agregar XP.",
    cantidad="Cantidad de XP a agregar (1 - 1.000.000)."
)
        
    @app_commands.checks.has_permissions(
        administrator=True
    )
    async def addxp(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        cantidad: app_commands.Range[int, 1, 1000000]
    ):
        # ====================================================
        # COMPROBAR SERVIDOR
        # ====================================================
        if interaction.guild is None:
            await interaction.response.send_message(
                "❌ Este comando solo funciona "
                "en servidores.",
                ephemeral=True
            )
            return
        # ====================================================
        # CARGAR DATOS
        # ====================================================
        data = load_data()
        guild_id = str(
            interaction.guild.id
        )
        user_id = str(
            usuario.id
        )
        # ====================================================
        # CREAR SERVIDOR
        # ====================================================
        if guild_id not in data:
            data[guild_id] = {}
        # ====================================================
        # CREAR USUARIO
        # ====================================================
        if user_id not in data[guild_id]:
            data[guild_id][user_id] = {
                "xp": 0,
                "level": 0
            }
        # ====================================================
        # DATOS ACTUALES
        # ====================================================
        user_data = data[guild_id][user_id]
        old_level = int(
            user_data.get(
                "level",
                0
            )
        )
        old_xp = int(
            user_data.get(
                "xp",
                0
            )
        )
        # ====================================================
        # AGREGAR XP
        # ====================================================
        new_total_xp = (
            old_xp
            +
            cantidad
        )
        # ====================================================
        # CALCULAR NIVEL
        # ====================================================
        new_level, remaining_xp = calculate_level(
            new_total_xp
        )
        # ====================================================
        # ACTUALIZAR DATOS
        # ====================================================
        user_data["level"] = new_level
        user_data["xp"] = remaining_xp
        # ====================================================
        # GUARDAR
        # ====================================================
        save_data(
            data
        )
        # ====================================================
        # embed
    # ========================================================
            # ====================================================
        # EMBED
        # ====================================================

        embed = discord.Embed(
            title="✨ XP agregada",
            description=(
                f"Se agregaron **{cantidad:,} XP** "
                f"a {usuario.mention}."
            ),
            colour=discord.Colour.green()
        )

        embed.add_field(
            name="📊 Información de XP",
            value=(
                f"✨ XP agregada: **{cantidad:,}**\n"
                f"📈 XP actual: **{remaining_xp:,}**\n"
                f"🎯 XP necesaria para el siguiente nivel: "
                f"**{xp_required(new_level):,}**"
            ),
            inline=False
        )

        embed.add_field(
            name="🏆 Nivel",
            value=(
                f"**{old_level}** → "
                f"**{new_level}**"
            ),
            inline=True
        )

        embed.add_field(
            name="✨ XP",
            value=(
                f"**{remaining_xp:,}** / "
                f"**{xp_required(new_level):,}**"
            ),
            inline=True
        )

        if new_level > old_level:

            embed.add_field(
                name="🎉 ¡Subió de nivel!",
                value=(
                    f"{usuario.mention} alcanzó "
                    f"el nivel **{new_level}**."
                ),
                inline=False
            )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        embed.set_footer(
            text=(
                f"XP agregada por "
                f"{interaction.user}"
            )
        )

        await interaction.response.send_message(
            embed=embed
        )
    # ERROR
    # ========================================================
    @addxp.error
    async def addxp_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            message = (
                "❌ No tenés permisos para usar "
                "este comando.\n\n"
                "Necesitás tener el permiso "
                "**Administrador**."
            )
        else:
            print(
                f"❌ Error en /addxp: "
                f"{type(error).__name__}: "
                f"{error}"
            )
            message = (
                "❌ Ocurrió un error al "
                "agregar XP."
            )
        if interaction.response.is_done():
            await interaction.followup.send(
                message,
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                message,
                ephemeral=True
            )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        AddXP(bot)
    )