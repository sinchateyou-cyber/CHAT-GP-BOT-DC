```python
import discord
from discord.ext import commands


class Decir(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="decir",
        description="Hace que el bot repita exactamente tu mensaje."
    )
    @commands.guild_only()
    async def decir(
        self,
        ctx: commands.Context,
        *,
        mensaje: str
    ):

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        await ctx.send(
            mensaje,
            allowed_mentions=discord.AllowedMentions.none()
        )


async def setup(bot):
    await bot.add_cog(
        Decir(bot)
    )
```
