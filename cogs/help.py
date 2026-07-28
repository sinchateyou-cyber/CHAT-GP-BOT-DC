import discord
from discord.ext import commands
class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="help", aliases=["ayuda", "comandos"])
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="✨ Centro de Ayuda",
            description=(
                "Bienvenido al centro de comandos de **tu servidor**.\n"
                "Usá los comandos de abajo para interactuar con el bot.\n\n"
                "⚡ **Prefijo:** `!`"
            ),
            color=discord.Color.blurple()
        )
        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`!ban` — Banea a un usuario\n"
                "`!kick` — Expulsa a un usuario\n"
                "`!mute` — Silencia a un usuario\n"
                "`!unmute` — Quita el silencio\n"
                "`!warn` — Advierte a un usuario\n"
                "`!clear` — Borra mensajes"
            ),
            inline=False
        )
        embed.add_field(
            name="💤 AFK",
            value=(
                "`!afk` — Activa tu estado AFK\n"
                "`!afk off` — Desactiva tu estado AFK"
            ),
            inline=False
        )
        embed.add_field(
            name="📊 Status",
            value=(
                "`!setstatus` — Configura el estado del bot\n"
                "`!clearstatus` — Elimina el estado personalizado"
            ),
            inline=False
        )
        embed.add_field(
            name="🎉 Bienvenida",
            value=(
                "`!setwelcome` — Configura el canal de bienvenida\n"
                "`!clearwelcome` — Elimina la configuración"
            ),
            inline=False
        )
        embed.add_field(
            name="🎭 Roles",
            value=(
                "`!addrole` — Añade un rol a un usuario\n"
                "`!removerole` — Quita un rol\n"
                "`!autorole` — Configura el rol automático"
            ),
            inline=False
        )
        embed.add_field(
            name="🔗 Bot",
            value=(
                "`!invite` — Invita el bot a otro servidor\n"
                "`!ping` — Comprueba la latencia\n"
                "`!serverinfo` — Información del servidor\n"
                "`!userinfo` — Información de un usuario"
            ),
            inline=False
        )
        embed.set_footer(
            text=f"Solicitado por {ctx.author}",
            icon_url=ctx.author.display_avatar.url
        )
        await ctx.send(embed=embed)
async def setup(bot):
    await bot.add_cog(Help(bot))