import discord
from discord import app_commands
from discord.ext import commands
class Nick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # CAMBIAR APODO
    # =========================
    @app_commands.command(
        name="nick",
        description="Cambia el apodo de un usuario."
    )
    @app_commands.describe(
        miembro="Usuario al que querés cambiarle el apodo.",
        apodo="Nuevo apodo que querés asignar."
    )
    @app_commands.checks.has_permissions(
        manage_nicknames=True
    )
    async def nick(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member,
        apodo: str
    ):
        # =========================
        # COMPROBAR JERARQUÍA
        # =========================
        if miembro.top_role >= interaction.user.top_role:
            await interaction.response.send_message(
                "❌ No podés cambiar el apodo de un usuario "
                "con un rol igual o superior al tuyo.",
                ephemeral=True
            )
            return
        # =========================
        # COMPROBAR JERARQUÍA DEL BOT
        # =========================
        if (
            interaction.guild.me
            and miembro.top_role >= interaction.guild.me.top_role
        ):
            await interaction.response.send_message(
                "❌ No puedo cambiar el apodo de ese usuario. "
                "Mi rol debe estar por encima del suyo.",
                ephemeral=True
            )
            return
        try:
            apodo_anterior = miembro.display_name
            await miembro.edit(
                nick=apodo,
                reason=(
                    f"Apodo cambiado por "
                    f"{interaction.user}"
                )
            )
            # =========================
            # EMBED
            # =========================
            embed = discord.Embed(
                title="✏️ Apodo cambiado",
                description=(
                    f"Se cambió el apodo de "
                    f"{miembro.mention}."
                ),
                color=discord.Color.blurple()
            )
            embed.add_field(
                name="👤 Usuario",
                value=miembro.mention,
                inline=True
            )
            embed.add_field(
                name="📝 Apodo anterior",
                value=apodo_anterior,
                inline=True
            )
            embed.add_field(
                name="✨ Nuevo apodo",
                value=apodo,
                inline=True
            )
            await interaction.response.send_message(
                embed=embed
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No puedo cambiar el apodo de ese usuario. "
                "Asegurate de que mi rol esté por encima del suyo.",
                ephemeral=True
            )
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Ocurrió un error al cambiar el apodo.",
                ephemeral=True
            )
    # =========================
    # ERROR DEL COMANDO
    # =========================
    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(
            error,
            app_commands.errors.MissingPermissions
        ):
            await interaction.response.send_message(
                "❌ Necesitás el permiso "
                "**Gestionar apodos** para usar este comando.",
                ephemeral=True
            )
        else:
            print(
                f"❌ Error en /nick: {error}"
            )
            if not interaction.response.is_done():
                await interaction.response.send_message(
                    "❌ Ocurrió un error al ejecutar el comando.",
                    ephemeral=True
                )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Nick(bot)
    )