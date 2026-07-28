import discord
from discord.ext import commands
from datetime import timedelta


class Moderacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # CLEAR
    # =========================

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, cantidad: int):

        if cantidad < 1 or cantidad > 100:
            await ctx.send(
                "❌ La cantidad debe estar entre 1 y 100."
            )
            return

        await ctx.channel.purge(
            limit=cantidad + 1
        )

        mensaje = await ctx.send(
            f"🗑️ Se eliminaron {cantidad} mensajes."
        )

        await mensaje.delete(delay=3)

    # =========================
    # KICK
    # =========================

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        miembro: discord.Member,
        *,
        razon="Sin razón"
    ):

        if miembro == ctx.author:
            await ctx.send(
                "❌ No podés expulsarte a vos mismo."
            )
            return

        if miembro.top_role >= ctx.author.top_role:
            await ctx.send(
                "❌ No podés expulsar a un usuario "
                "con un rol igual o superior al tuyo."
            )
            return

        if miembro.top_role >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ Mi rol está por debajo del rol "
                "de ese usuario."
            )
            return

        await miembro.kick(reason=razon)

        await ctx.send(
            f"👢 {miembro.mention} fue expulsado.\n"
            f"📝 Razón: {razon}"
        )

    # =========================
    # BAN
    # =========================

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        miembro: discord.Member,
        *,
        razon="Sin razón"
    ):

        if miembro == ctx.author:
            await ctx.send(
                "❌ No podés banearte a vos mismo."
            )
            return

        if miembro.top_role >= ctx.author.top_role:
            await ctx.send(
                "❌ No podés banear a un usuario "
                "con un rol igual o superior al tuyo."
            )
            return

        if miembro.top_role >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ Mi rol está por debajo del rol "
                "de ese usuario."
            )
            return

        await miembro.ban(reason=razon)

        await ctx.send(
            f"🔨 {miembro.mention} fue baneado.\n"
            f"📝 Razón: {razon}"
        )

    # =========================
    # UNBAN
    # =========================

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(
        self,
        ctx,
        usuario_id: int
    ):

        try:
            usuario = await self.bot.fetch_user(
                usuario_id
            )

            await ctx.guild.unban(
                usuario
            )

            await ctx.send(
                f"✅ {usuario} fue desbaneado."
            )

        except discord.NotFound:
            await ctx.send(
                "❌ Ese usuario no está baneado "
                "o el ID no es válido."
            )

    # =========================
    # TIMEOUT
    # =========================

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx,
        miembro: discord.Member,
        minutos: int,
        *,
        razon="Sin razón"
    ):

        if minutos < 1 or minutos > 40320:
            await ctx.send(
                "❌ El tiempo debe ser entre "
                "1 minuto y 28 días."
            )
            return

        if miembro == ctx.author:
            await ctx.send(
                "❌ No podés aplicarte timeout a vos mismo."
            )
            return

        if miembro.top_role >= ctx.author.top_role:
            await ctx.send(
                "❌ No podés aplicar timeout a un usuario "
                "con un rol igual o superior al tuyo."
            )
            return

        await miembro.timeout(
            timedelta(minutes=minutos),
            reason=razon
        )

        await ctx.send(
            f"🔇 {miembro.mention} recibió timeout.\n"
            f"⏱️ Duración: {minutos} minutos\n"
            f"📝 Razón: {razon}"
        )

    # =========================
    # UNTIMEOUT
    # =========================

    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(
        self,
        ctx,
        miembro: discord.Member
    ):

        await miembro.timeout(None)

        await ctx.send(
            f"🔊 Se quitó el timeout a "
            f"{miembro.mention}."
        )

    # =========================
    # LOCK
    # =========================

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )

        await ctx.send(
            "🔒 Canal bloqueado."
        )

    # =========================
    # UNLOCK
    # =========================

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=None
        )

        await ctx.send(
            "🔓 Canal desbloqueado."
        )

    # =========================
    # MANEJO DE ERRORES
    # =========================

    @clear.error
    @kick.error
    @ban.error
    @unban.error
    @timeout.error
    @untimeout.error
    @lock.error
    @unlock.error
    async def errores(
        self,
        ctx,
        error
    ):

        if isinstance(
            error,
            commands.MissingPermissions
        ):
            await ctx.send(
                "❌ No tenés permisos "
                "para usar este comando."
            )

        elif isinstance(
            error,
            commands.MemberNotFound
        ):
            await ctx.send(
                "❌ No encontré a ese usuario."
            )

        elif isinstance(
            error,
            commands.UserNotFound
        ):
            await ctx.send(
                "❌ No encontré ese usuario."
            )

        elif isinstance(
            error,
            commands.MissingRequiredArgument
        ):
            await ctx.send(
                "❌ Faltan argumentos. "
                "Usá `!ayuda` para ver cómo usar los comandos."
            )

        elif isinstance(
            error,
            commands.BadArgument
        ):
            await ctx.send(
                "❌ El formato del comando es incorrecto."
            )

        else:
            print(
                f"❌ Error de moderación: {error}"
            )


async def setup(bot):
    await bot.add_cog(
        Moderacion(bot)
    )