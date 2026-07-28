import discord
from discord import app_commands
from discord.ext import commands
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # HELP / AYUDA
    # =========================
    @app_commands.command(
        name="help",
        description="Muestra todos los comandos disponibles."
    )
    async def help_command(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="✨ Centro de Ayuda",
            description=(
                "Bienvenido al centro de comandos de **tu servidor**.\n"
                "Usá los comandos de abajo para interactuar con el bot.\n\n"
                "⚡ **Prefijo:** `/`"
            ),
            color=discord.Color.blurple()
        )
        # =========================
        # MODERACIÓN
        # =========================
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`/ban` — Banea a un usuario\n"
                "`/kick` — Expulsa a un usuario\n"
                "`/mute` — Silencia a un usuario\n"
                "`/unmute` — Quita el silencio\n"
                "`/warn` — Advierte a un usuario\n"
                "`/clear` — Borra mensajes"
            ),
            inline=False
        )
        # =========================
        # AFK
        # =========================
        embed.add_field(
            name="💤 AFK",
            value=(
                "`/afk` — Activa o desactiva tu estado AFK"
            ),
            inline=False
        )
        # =========================
        # STATUS
        # =========================
        embed.add_field(
            name="📊 Status",
            value=(
                "`/setstatus` — Configura el estado del bot\n"
                "`/clearstatus` — Elimina el estado personalizado"
            ),
            inline=False
        )
        # =========================
        # BIENVENIDA
        # =========================
        embed.add_field(
            name="🎉 Bienvenida",
            value=(
                "`/setwelcome` — Configura el canal de bienvenida\n"
                "`/clearwelcome` — Elimina la configuración"
            ),
            inline=False
        )
        # =========================
        # ROLES
        # =========================
        embed.add_field(
            name="🎭 Roles",
            value=(
                "`/addrole` — Añade un rol a un usuario\n"
                "`/removerole` — Quita un rol\n"
                "`/autorole` — Configura el rol automático"
            ),
            inline=False
        )
        # =========================
        # UTILIDADES
        # =========================
        embed.add_field(
            name="🛠️ Utilidades",
            value=(
                "`/ping` — Comprueba la latencia\n"
                "`/avatar` — Muestra el avatar\n"
                "`/serverinfo` — Información del servidor\n"
                "`/userinfo` — Información de un usuario"
            ),
            inline=False
        )
        # =========================
        # BOT
        # =========================
        embed.add_field(
            name="🤖 Bot",
            value=(
                "`/invite` — Invita el bot a otro servidor\n"
                "`/say` — Hace que el bot envíe un mensaje\n"
                "`/owner` — Muestra información del dueño"
            ),
            inline=False
        )
        # =========================
        # VERIFICACIÓN
        # =========================
        embed.add_field(
            name="✅ Verificación",
            value=(
                "`/verificacion` — Envía el panel de verificación"
            ),
            inline=False
        )
        # =========================
        # FOOTER
        # =========================
        embed.set_footer(
            text=f"Solicitado por {interaction.user}",
            icon_url=interaction.user.display_avatar.url
        )
        await interaction.response.send_message(
            embed=embed
        )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Help(bot)
    )