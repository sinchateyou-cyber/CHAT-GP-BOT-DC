import discord
from discord.ext import commands
class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="invite")
    async def invite(self, ctx):
        """Genera el enlace para invitar el bot."""
        invite_url = discord.utils.oauth_url(
            self.bot.user.id,
            permissions=discord.Permissions(administrator=True)
        )
        embed = discord.Embed(
            title="🤖 ¡Invitá mi bot!",
            description=f"[Hacé clic acá para invitarme a tu servidor]({invite_url})",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)
async def setup(bot):
    await bot.add_cog(Invite(bot))