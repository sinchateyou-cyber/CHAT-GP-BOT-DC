import discord
from discord.ext import commands
class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="setstatus")
    @commands.has_permissions(administrator=True)
    async def setstatus(self, ctx, *, texto: str):
        await self.bot.change_presence(
            activity=discord.Game(name=texto)
        )
        await ctx.send(
            f"✅ Estado cambiado correctamente a: **{texto}**"
        )
    @commands.command(name="clearstatus")
    @commands.has_permissions(administrator=True)
    async def clearstatus(self, ctx):
        await self.bot.change_presence(
            activity=discord.Seeing(
                name="s!ayuda $$$"
            )
        )
        await ctx.send(
            "✅ Estado personalizado eliminado. Volví al estado predeterminado."
        )
    @setstatus.error
    async def setstatus_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ Necesitás permisos de **Administrador** para usar este comando."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ Tenés que escribir el estado.\n"
                "Ejemplo: `s!setstatus Jugando Free Fire`"
            )
    @clearstatus.error
    async def clearstatus_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ Necesitás permisos de **Administrador** para usar este comando."
            )
async def setup(bot):
    await bot.add_cog(Status(bot))