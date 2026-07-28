import discord
from discord.ext import commands


class Status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setstatus")
    async def setstatus(self, ctx, *, texto=None):

        if texto is None:
            await ctx.send(
                "❌ Uso correcto: `s!setstatus Tu estado`"
            )
            return

        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(name=texto)
        )

        await ctx.send(
            f"✅ Estado cambiado a: **{texto}**"
        )

    @commands.command(name="clearstatus")
    async def clearstatus(self, ctx):

        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Seeing(
                name="s!ayuda $$$"
            )
        )

        await ctx.send(
            "✅ Estado restablecido."
        )


async def setup(bot):
    await bot.add_cog(Status(bot))