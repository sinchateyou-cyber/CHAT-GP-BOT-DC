import discord
from discord.ext import commands


class Utilidades(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # PING
    # =========================

    @commands.command()
    async def ping(self, ctx):

        ms = round(
            self.bot.latency * 1000
        )

        await ctx.send(
            f"🏓 Pong! `{ms}ms`"
        )

    # =========================
    # AVATAR
    # =========================

    @commands.command()
    async def avatar(
        self,
        ctx,
        miembro: discord.Member = None
    ):

        miembro = miembro or ctx.author

        embed = discord.Embed(
            title=f"🖼️ Avatar de {miembro}"
        )

        embed.set_image(
            url=miembro.display_avatar.url
        )

        await ctx.send(
            embed=embed
        )

    # =========================
    # USERINFO
    # =========================

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

        await ctx.send(
            embed=embed
        )

    # =========================
    # SERVERINFO
    # =========================

    @commands.command()
    async def serverinfo(self, ctx):

        servidor = ctx.guild

        embed = discord.Embed(
            title=f"📊 {servidor.name}"
        )

        if servidor.icon:
            embed.set_thumbnail(
                url=servidor.icon.url
            )

        embed.add_field(
            name="👑 Dueño",
            value=servidor.owner.mention
            if servidor.owner
            else "Desconocido",
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

        await ctx.send(
            embed=embed
        )

    # =========================
    # AYUDA
    # =========================

    @commands.command(
        name="ayuda",
        aliases=["help", "comandos"]
    )
    async def ayuda(self, ctx):

        embed = discord.Embed(
            title="🤖 Centro de comandos",
            description=(
                "Estos son los comandos disponibles "
                "en el servidor."
            )
        )

        embed.add_field(
            name="🛡️ Moderación",
            value=(
                "`!clear 10`\n"
                "`!kick @usuario razón`\n"
                "`!ban @usuario razón`\n"
                "`!unban ID`\n"
                "`!timeout @usuario 10 razón`\n"
                "`!untimeout @usuario`\n"
                "`!lock`\n"
                "`!unlock`"
            ),
            inline=False
        )

        embed.add_field(
            name="💤 AFK",
            value=(
                "`!afk motivo`"
            ),
            inline=False
        )

        embed.add_field(
            name="🎭 Roles",
            value=(
                "`!autorole @rol`\n"
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
            value=(
                "`!verificacion`"
            ),
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

        embed.set_footer(
            text="Usá los comandos respetando las reglas del servidor."
        )

        await ctx.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Utilidades(bot)
    )