import discord
from discord.ext import commands


class Imagenes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="publicarimagen",
        description="Publica una imagen usando su URL."
    )
    @commands.guild_only()
    async def publicarimagen(
        self,
        ctx: commands.Context,
        url: str
    ):

        # Comprobación básica de URL
        if not url.startswith(("http://", "https://")):
            return await ctx.send(
                "❌ Tenés que proporcionar una URL válida.",
                ephemeral=True
            )

        embed = discord.Embed()

        embed.set_image(url=url)

        try:
            await ctx.send(
                embed=embed
            )

            # Intentar borrar el comando original
            try:
                await ctx.message.delete()
            except (discord.Forbidden, discord.NotFound):
                pass

        except discord.HTTPException:
            await ctx.send(
                "❌ No pude cargar esa imagen. "
                "Comprobá que la URL sea directa y termine en una extensión compatible.",
                ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(
        Imagenes(bot)
    )
