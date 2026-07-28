import discord
from discord.ext import commands


class Status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.status_actual = None

    @commands.command(name="estado")
    @commands.has_permissions(administrator=True)
    async def setstatus(self, ctx, *, texto: str):

        self.status_actual = texto

        await self.bot.change_presence(
            activity=discord.Game(
                name=texto
            )
        )

        await ctx.send(
            f"✅ Estado cambiado a: **{texto}**"
        )

    @commands.command(name="clearstatus")
    @commands.has_permissions(administrator=True)
    async def clearstatus(self, ctx):

        self.status_actual = None

        await self.bot.change_presence(
            activity=discord.Seeing(
                name="s!ayuda $$$"
            )
        )

        await ctx.send(
            "✅ Estado personalizado eliminado."
        )


async def setup(bot):
    await bot.add_cog(Status(bot))