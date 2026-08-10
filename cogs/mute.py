import re
from datetime import timedelta

import discord
from discord.ext import commands
from discord import app_commands


# ============================================================
# CONVERSOR DE TIEMPO
# ============================================================

def parse_duration(text: str) -> int | None:
    """
    Convierte:
    10s -> 10 segundos
    10m -> 10 minutos
    2h  -> 2 horas
    1d  -> 1 día
    1w  -> 1 semana
    """

    match = re.fullmatch(
        r"(\d+)\s*(s|m|h|d|w)",
        text.lower().strip()
    )

    if not match:
        return None

    amount = int(match.group(1))
    unit = match.group(2)

    multipliers = {
        "s": 1,
        "m": 60,
        "h": 60 * 60,
        "d": 60 * 60 * 24,
        "w": 60 * 60 * 24 * 7
    }

    return amount * multipliers[unit]


# ============================================================
# COG MUTE
# ============================================================

class Mute(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ========================================================
    # /mute
    # ========================================================

    @app_commands.command(
        name="mute",
        description="Aplica un timeout temporal a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario que querés mutear.",
        tiempo="Duración: 10s, 10m, 2h, 1d o 1w.",
        razon="Razón del mute."
    )
    @app_commands.default_permissions(moderate_members=True)
    async def mute(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        tiempo: str,
        razon: str = "Sin razón especificada"
    ):

        # ----------------------------------------------------
        # Comprobar permisos del bot
        # ----------------------------------------------------

        if not interaction.guild.me.guild_permissions.moderate_members:
            return await interaction.response.send_message(
                "❌ No tengo permiso para moderar miembros.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # No mutear al propio bot
        # ----------------------------------------------------

        if usuario.id == self.bot.user.id:
            return await interaction.response.send_message(
                "❌ No puedo mutearme a mí mismo.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # No mutear al dueño del servidor
        # ----------------------------------------------------

        if usuario.id == interaction.guild.owner_id:
            return await interaction.response.send_message(
                "❌ No podés aplicar timeout al dueño del servidor.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # Comprobar jerarquía
        # ----------------------------------------------------

        if usuario.top_role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ No puedo aplicar timeout a ese usuario porque "
                "su rol más alto es igual o superior al mío.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # Comprobar jerarquía del moderador
        # ----------------------------------------------------

        if (
            interaction.user.id != interaction.guild.owner_id
            and usuario.top_role >= interaction.user.top_role
        ):
            return await interaction.response.send_message(
                "❌ No podés aplicar timeout a alguien con un rol "
                "igual o superior al tuyo.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # Convertir tiempo
        # ----------------------------------------------------

        seconds = parse_duration(tiempo)

        if seconds is None:
            return await interaction.response.send_message(
                "❌ Tiempo inválido.\n\n"
                "Usá formatos como:\n"
                "`10s` → 10 segundos\n"
                "`10m` → 10 minutos\n"
                "`2h` → 2 horas\n"
                "`1d` → 1 día\n"
                "`1w` → 1 semana",
                ephemeral=True
            )

        # Discord permite un máximo de 28 días
        if seconds > 28 * 24 * 60 * 60:
            return await interaction.response.send_message(
                "❌ El timeout máximo de Discord es de **28 días**.",
                ephemeral=True
            )

        if seconds <= 0:
            return await interaction.response.send_message(
                "❌ El tiempo debe ser mayor a 0.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # Aplicar timeout
        # ----------------------------------------------------

        duration = timedelta(seconds=seconds)

        try:
            await usuario.timeout(
                duration,
                reason=razon
            )

        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ Discord rechazó la acción. Revisá mis permisos "
                "y la posición de mis roles.",
                ephemeral=True
            )

        except discord.HTTPException:
            return await interaction.response.send_message(
                "❌ Ocurrió un error al aplicar el timeout.",
                ephemeral=True
            )

        # ----------------------------------------------------
        # Embed de confirmación
        # ----------------------------------------------------

        embed = discord.Embed(
            title="🔇 Usuario muteado",
            description=(
                f"**Usuario:** {usuario.mention}\n"
                f"**Duración:** `{tiempo}`\n"
                f"**Razón:** {razon}\n"
                f"**Moderador:** {interaction.user.mention}"
            ),
            color=discord.Color.orange()
        )

        embed.set_thumbnail(
            url=usuario.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )

        # ----------------------------------------------------
        # DM al usuario
        # ----------------------------------------------------

        try:
            dm_embed = discord.Embed(
                title="🔇 Fuiste muteado",
                description=(
                    f"Fuiste muteado en **{interaction.guild.name}**.\n\n"
                    f"**Duración:** `{tiempo}`\n"
                    f"**Razón:** {razon}"
                ),
                color=discord.Color.orange()
            )

            await usuario.send(embed=dm_embed)

        except discord.Forbidden:
            pass

    # ========================================================
    # /unmute
    # ========================================================

    @app_commands.command(
        name="unmute",
        description="Quita el timeout de un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que querés quitarle el timeout."
    )
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member
    ):

        if not usuario.is_timed_out():
            return await interaction.response.send_message(
                "❌ Ese usuario no tiene un timeout activo.",
                ephemeral=True
            )

        if (
            interaction.user.id != interaction.guild.owner_id
            and usuario.top_role >= interaction.user.top_role
        ):
            return await interaction.response.send_message(
                "❌ No podés quitarle el timeout a ese usuario.",
                ephemeral=True
            )

        try:
            await usuario.timeout(
                None,
                reason=f"Timeout removido por {interaction.user}"
            )

        except discord.Forbidden:
            return await interaction.response.send_message(
                "❌ No tengo permisos para quitar el timeout.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🔊 Timeout removido",
            description=(
                f"**Usuario:** {usuario.mention}\n"
                f"**Moderador:** {interaction.user.mention}"
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(
            embed=embed
        )


# ============================================================
# SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Mute(bot))