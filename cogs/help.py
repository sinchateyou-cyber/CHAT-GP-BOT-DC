import discord
from discord import app_commands
from discord.ext import commands
class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    @app_commands.command(
        name="help",
        description="Muestra el centro de ayuda y todos los comandos."
    )
    async def help(
        self,
        interaction: discord.Interaction
    ):
        embed = discord.Embed(
            title="💎 Centro de Ayuda",
            description=(
                f"Bienvenido al centro de ayuda de **{self.bot.user.name}**.\n\n"
                "Usá los comandos de abajo para administrar y disfrutar tu servidor."
            ),
            color=discord.Color.blurple()
        )
        # 🛡️ MODERACIÓN
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`/ban` • `/kick`\n"
                "`/timeout` • `/untimeout`\n"
                "`/clear` • `/lock` • `/unlock`"
            ),
            inline=True
        )
        # 🎵 MÚSICA
        embed.add_field(
            name="🎵 Música",
            value=(
                "`/play` • `/stop`\n"
                "`/leave`"
            ),
            inline=True
        )
        # ⚙️ CONFIGURACIÓN
        embed.add_field(
            name="⚙️ Configuración",
            value=(
                "`/config`\n"
                "`/setstatus`\n"
                "`/addrole` • `/createrole`\n"
                "`/deleterole`"
            ),
            inline=True
        )
        # 🛠️ UTILIDADES
        embed.add_field(
            name="🛠️ Utilidades",
            value=(
                "`/avatar` • `/userinfo`\n"
                "`/say` • `/nick`\n"
                "`/addemoji`"
            ),
            inline=True
        )
        # 🛡️ SEGURIDAD
        embed.add_field(
            name="🔒 Seguridad",
            value=(
                "AntiSpam\n"
                "AntiFlood\n"
                "AntiLink\n"
                "Logs"
            ),
            inline=True
        )
        # 🎫 SERVIDOR
        embed.add_field(
            name="🎫 Servidor",
            value=(
                "`/afk`\n"
                "`/invite`\n"
                "`/invites`\n"
                "`/leaderboard`\n"
                "Tickets • Verificación"
            ),
            inline=True
        )
        # 🤖 INFORMACIÓN
        embed.add_field(
            name="🤖 Información",
            value=(
                "`/botinfo`\n"
                "`/help`\n"
                "`/owner`"
            ),
            inline=True
        )
        # 📌 FOOTER
        embed.set_footer(
            text=(
                f"{self.bot.user.name} • "
                f"Solicitado por {interaction.user.display_name}"
            ),
            icon_url=self.bot.user.display_avatar.url
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(
            embed=embed
        )
async def setup(bot: commands.Bot):
    await bot.add_cog(
        Help(bot)
    )