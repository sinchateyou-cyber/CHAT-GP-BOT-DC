import discord
from discord import app_commands
from discord.ext import commands
class Utilidades(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # PING
    # =========================
    @app_commands.command(
        name="ping",
        description="Muestra la latencia del bot."
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):
        ms = round(
            self.bot.latency * 1000
        )
        await interaction.response.send_message(
            f"🏓 Pong! `{ms}ms`"
        )
    # =========================
    # AVATAR
    # =========================
    @app_commands.command(
        name="avatar",
        description="Muestra el avatar de un usuario."
    )
    @app_commands.describe(
        miembro="Usuario del que querés ver el avatar."
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member = None
    ):
        miembro = miembro or interaction.user
        embed = discord.Embed(
            title=f"🖼️ Avatar de {miembro}"
        )
        embed.set_image(
            url=miembro.display_avatar.url
        )
        await interaction.response.send_message(
            embed=embed
        )
    # =========================
    # USERINFO
    # =========================
    @app_commands.command(
        name="userinfo",
        description="Muestra información de un usuario."
    )
    @app_commands.describe(
        miembro="Usuario del que querés ver la información."
    )
    async def userinfo(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member = None
    ):
        miembro = miembro or interaction.user
        embed = discord.Embed(
            title="👤 Información del usuario"
        )
        embed.set_thumbnail(
            url=miembro.display_avatar.url
        )
        embed.add_field(
            name="👤 Usuario",
            value=miembro.mention,
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=str(miembro.id),
            inline=True
        )
        embed.add_field(
            name="🤖 Bot",
            value="Sí" if miembro.bot else "No",
            inline=True
        )
        embed.add_field(
            name="📅 Cuenta creada",
            value=discord.utils.format_dt(
                miembro.created_at,
                style="D"
            ),
            inline=False
        )
        embed.add_field(
            name="📥 Entró al servidor",
            value=(
                discord.utils.format_dt(
                    miembro.joined_at,
                    style="D"
                )
                if miembro.joined_at
                else "Desconocido"
            ),
            inline=False
        )
        await interaction.response.send_message(
            embed=embed
        )
    # =========================
    # SERVERINFO
    # =========================
    @app_commands.command(
        name="serverinfo",
        description="Muestra información del servidor."
    )
    async def serverinfo(
        self,
        interaction: discord.Interaction
    ):
        servidor = interaction.guild
        if servidor is None:
            await interaction.response.send_message(
                "❌ Este comando solo puede usarse dentro de un servidor.",
                ephemeral=True
            )
            return
        embed = discord.Embed(
            title=f"📊 {servidor.name}"
        )
        if servidor.icon:
            embed.set_thumbnail(
                url=servidor.icon.url
            )
        embed.add_field(
            name="👑 Dueño",
            value=(
                servidor.owner.mention
                if servidor.owner
                else "Desconocido"
            ),
            inline=True
        )
        embed.add_field(
            name="👥 Miembros",
            value=str(
                servidor.member_count
            ),
            inline=True
        )
        embed.add_field(
            name="📁 Canales",
            value=str(
                len(servidor.channels)
            ),
            inline=True
        )
        embed.add_field(
            name="🎭 Roles",
            value=str(
                len(servidor.roles)
            ),
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=str(
                servidor.id
            ),
            inline=True
        )
        embed.add_field(
            name="📅 Creado",
            value=discord.utils.format_dt(
                servidor.created_at,
                style="D"
            ),
            inline=True
        )
        await interaction.response.send_message(
            embed=embed
        )
    # =========================
    # AYUDA
    # =========================
    @app_commands.command(
        name="help",
        description="Muestra todos los comandos disponibles."
    )
    async def help(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="🤖 Centro de Ayuda",
            description=(
                f"Hola {interaction.user.mention}, "
                "acá tenés todos los comandos disponibles."
            )
        )
        # =========================
        # MODERACIÓN
        # =========================
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`/clear`\n"
                "`/kick`\n"
                "`/ban`\n"
                "`/unban`\n"
                "`/timeout`\n"
                "`/untimeout`\n"
                "`/lock`\n"
                "`/unlock`\n"
                "`/nick`"
            ),
            inline=False
        )
        # =========================
        # AFK
        # =========================
        embed.add_field(
            name="💤 AFK",
            value=(
                "`/afk`"
            ),
            inline=False
        )
        # =========================
        # ROLES
        # =========================
        embed.add_field(
            name="🎭 Roles",
            value=(
                "`/autorole`\n"
                "`/addrole`\n"
                "`/removerole`"
            ),
            inline=False
        )
        # =========================
        # TICKETS
        # =========================
        embed.add_field(
            name="🎫 Tickets",
            value=(
                "`/ticketpanel`\n"
                "`/closeticket`"
            ),
            inline=False
        )
        # =========================
        # VERIFICACIÓN
        # =========================
        embed.add_field(
            name="✅ Verificación",
            value=(
                "`/verificacion`"
            ),
            inline=False
        )
        # =========================
        # UTILIDADES
        # =========================
        embed.add_field(
            name="🛠️ Utilidades",
            value=(
                "`/ping`\n"
                "`/avatar`\n"
                "`/userinfo`\n"
                "`/serverinfo`\n"
                "`/help`"
            ),
            inline=False
        )
        # =========================
        # OTROS
        # =========================
        embed.add_field(
            name="📢 Otros",
            value=(
                "`/say`\n"
                "`/owner`\n"
                "`/invite`"
            ),
            inline=False
        )
        embed.set_footer(
            text="Usá los comandos respetando las reglas del servidor."
        )
        await interaction.response.send_message(
            embed=embed
        )
# =========================
# CARGAR COG
# =========================
async def setup(bot):
    await bot.add_cog(
        Utilidades(bot)
    )