import discord
from discord.ext import commands


class Utilidades(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def ping(self, ctx):

        ms = round(
            self.bot.latency * 1000
        )

        await ctx.send(
            f"🏓 Pong! `{ms}ms`"
        )


    @commands.command()
    async def avatar(
        self,
        ctx,
        miembro: discord.Member = None
    ):

        miembro = miembro or ctx.author

        embed = discord.Embed(
            title=f"Avatar de {miembro}"
        )

        embed.set_image(
            url=miembro.display_avatar.url
        )

        await ctx.send(
            embed=embed
        )


    @commands.command()
    async def userinfo(
        self,
        ctx,
        miembro: discord.Member = None
    ):

        miembro = miembro or ctx.author

        embed = discord.Embed(
            title="👤 Información del usuario"
        )

        embed.add_field(
            name="Usuario",
            value=miembro
        )

        embed.add_field(
            name="ID",
            value=miembro.id
        )

        embed.add_field(
            name="Cuenta creada",
            value=discord.utils.format_dt(
                miembro.created_at,
                style="D"
            )
        )

        await ctx.send(
            embed=embed
        )


    @commands.command()
    async def serverinfo(self, ctx):

        servidor = ctx.guild

        embed = discord.Embed(
            title=f"📊 {servidor.name}"
        )

        embed.add_field(
            name="👥 Miembros",
            value=servidor.member_count
        )

        embed.add_field(
            name="🆔 ID",
            value=servidor.id
        )

        embed.add_field(
            name="📁 Canales",
            value=len(servidor.channels)
        )

        await ctx.send(
            embed=embed
        )


    @commands.command(
        name="ayuda"
    )
    async def ayuda(self, ctx):

        embed = discord.Embed(
            title="🤖 Comandos del Bot",
            description=(
                "Lista de comandos disponibles"
            )
        )

        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`!clear 10`\n"
                "`!kick @usuario`\n"
                "`!ban @usuario`\n"
                "`!unban usuario`\n"
                "`!timeout @usuario 10`\n"
                "`!untimeout @usuario`\n"
                "`!lock`\n"
                "`!unlock`"
            ),
            inline=False
        )

        embed.add_field(
            name="🎭 Roles",
            value=(
                "`!addrole @usuario @rol`\n"
                "`!removerole @usuario @rol`"
            ),
            inline=False
        )

        embed.add_field(
            name="🎫 Tickets",
            value=(
                "`!ticketpanel`\n"
                "`!closeticket`"
            ),
            inline=False
        )

        embed.add_field(
            name="✅ Verificación",
            value="`!verificacion`",
            inline=False
        )

        embed.add_field(
            name="🛠️ Utilidades",
            value=(
                "`!ping`\n"
                "`!avatar`\n"
                "`!userinfo`\n"
                "`!serverinfo`"
            ),
            inline=False
        )

        await ctx.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Utilidades(bot)
    )