import discord
from discord import app_commands
from discord.ext import commands
# ============================================================
# COG HELP
# ============================================================
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ========================================================
    # /HELP
    # ========================================================
    @app_commands.command(
        name="help",
        description=(
            "Muestra todos los comandos "
            "disponibles del bot."
        )
    )
    async def help(
        self,
        interaction: discord.Interaction
    ):
        # ====================================================
        # CREAR EMBED
        # ====================================================
        embed = discord.Embed(
            title="💎 Centro de Ayuda",
            description=(
                "¡Bienvenido al centro de ayuda!\n\n"
                "Usá las categorías de abajo para "
                "conocer las funciones disponibles "
                "del bot."
            ),
            colour=discord.Colour.blurple()
        )
        # ====================================================
        # MODERACIÓN
        # ====================================================
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`/ban` • Banear un usuario\n"
                "`/kick` • Expulsar un usuario\n"
                "`/timeout` • Silenciar temporalmente\n"
                "`/untimeout` • Quitar el silencio\n"
                "`/clear` • Eliminar mensajes\n"
                "`/lock` • Bloquear un canal\n"
                "`/unlock` • Desbloquear un canal"
            ),
            inline=False
        )
        # ====================================================
        # XP Y NIVELES
        # ====================================================
        embed.add_field(
            name="🏆 XP y Niveles",
            value=(
                "`/level` • Ver tu nivel y XP\n"
                "`/rank` • Ver el ranking del servidor\n"
                "`/xprewards` • Ver recompensas por nivel\n"
                "`/addxp` • Agregar XP a un usuario\n"
                "`/addlevel` • Agregar niveles a un usuario"
            ),
            inline=False
        )
        # ====================================================
        # SOCIAL
        # ====================================================
        embed.add_field(
            name="💖 Social",
            value=(
                "`/abrazo` • Abrazar a un usuario\n"
                "`/beso` • Dar un beso\n"
                "`/acariciar` • Acariciar a un usuario\n"
                "`/cachetada` • Dar una cachetada\n"
                "`/morder` • Morder a un usuario\n"
                "`/cosquillas` • Hacer cosquillas\n"
                "`/saludar` • Saludar\n"
                "`/highfive` • Chocar los cinco\n"
                "`/guiño` • Guiñar el ojo\n"
                "`/pat` • Dar pat pat"
            ),
            inline=False
        )
        # ====================================================
        # UTILIDADES
        # ====================================================
        embed.add_field(
            name="🔧 Utilidades",
            value=(
                "`/ping` • Ver la latencia del bot\n"
                "`/avatar` • Ver el avatar de un usuario\n"
                "`/userinfo` • Ver información de un usuario\n"
                "`/botinfo` • Ver información del bot"
            ),
            inline=False
        )
        # ====================================================
        # CONFIGURACIÓN
        # ====================================================
        embed.add_field(
            name="⚙️ Configuración",
            value=(
                "`/server-setup` • Configurar el servidor\n"
                "`/config` • Configurar opciones del servidor\n"
                "`/verification` • Configurar verificación"
            ),
            inline=False
        )
        # ====================================================
        # SISTEMA DE MÚSICA
        # ====================================================
        embed.add_field(
            name="🎵 Música",
            value=(
                "🚧 **Sistema de música actualmente "
                "en mantenimiento.**\n\n"
                "El sistema de música se encuentra "
                "temporalmente deshabilitado mientras "
                "realizamos mejoras."
            ),
            inline=False
        )
        # ====================================================
        # SEGURIDAD
        # ====================================================
        embed.add_field(
            name="🛡️ Seguridad",
            value=(
                "🚨 Anti-Spam\n"
                "🔗 Anti-Link\n"
                "🌊 Anti-Flood"
            ),
            inline=False
        )
        # ====================================================
        # INVITACIONES
        # ====================================================
        embed.add_field(
            name="📨 Invitaciones",
            value=(
                "`/invite` • Invitar el bot\n"
                "`/invites` • Ver invitaciones\n"
                "`/invites-leaderboard` • Ranking de invitaciones"
            ),
            inline=False
        )
        # ====================================================
        # PIE DEL EMBED
        # ====================================================
        embed.set_footer(
            text=(
                f"Solicitado por "
                f"{interaction.user.display_name}"
            )
        )
        # ====================================================
        # AVATAR DEL USUARIO
        # ====================================================
        embed.set_thumbnail(
            url=(
                interaction.user
                .display_avatar
                .url
            )
        )
        # ====================================================
        # ENVIAR
        # ====================================================
        await interaction.response.send_message(
            embed=embed
        )
# ============================================================
# SETUP
# ============================================================
async def setup(bot):
    await bot.add_cog(
        Help(bot)
    )
    print(
        "✅ Sistema de ayuda cargado correctamente"
    )