import discord
from discord.ext import commands
from datetime import timedelta


class Moderacion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


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


    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        miembro: discord.Member,
        *,
        razon="Sin razón"
    ):

        await miembro.kick(reason=razon)

        await ctx.send(
            f"👢 {miembro.mention} fue expulsado.\n"
            f"📝 Razón: {razon}"
        )


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        miembro: discord.Member,
        *,
        razon="Sin razón"
    ):

        await miembro.ban(reason=razon)

        await ctx.send(
            f"🔨 {miembro.mention} fue baneado.\n"
            f"📝 Razón: {razon}"
        )


    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, nombre):

        baneados = [
            entrada async for entrada
            in ctx.guild.bans()
        ]

        encontrado = None

        for entrada in baneados:
            usuario = entrada.user

            if str(usuario) == nombre:
                encontrado = usuario
                break

        if encontrado is None:
            await ctx.send(
                "❌ No encontré a ese usuario en la lista de baneados."
            )
            return

        await ctx.guild.unban(encontrado)

        await ctx.send(
            f"✅ {encontrado} fue desbaneado."
        )


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
                "❌ El tiempo debe estar entre 1 minuto y 28 días."
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


    @commands.command()
    @commands.has_permissions(moderate_members=True)
    async def untimeout(
        self,
        ctx,
        miembro: discord.Member
    ):

        await miembro.timeout(None)

        await ctx.send(
            f"🔊 Timeout removido a {miembro.mention}."
        )


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )

        await ctx.send(
            "🔒 Este canal fue bloqueado."
        )


    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx):

        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=None
        )

        await ctx.send(
            "🔓 Este canal fue desbloqueado."
        )


    @clear.error
    @kick.error
    @ban.error
    @unban.error
    @timeout.error
    @untimeout.error
    @lock.error
    @unlock.error
    async def error_moderacion(self, ctx, error):

        if isinstance(
            error,
            commands.MissingPermissions
        ):
            await ctx.send(
                "❌ No tenés permisos para usar este comando."
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
            commands.MissingRequiredArgument
        ):
            await ctx.send(
                "❌ Faltan argumentos."
            )


async def setup(bot):
    await bot.add_cog(
        Moderacion(bot)
    )