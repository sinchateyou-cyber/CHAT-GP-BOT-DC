import discord
from discord.ext import commands


class Bienvenida(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_member_join(self, miembro):

        canal = discord.utils.get(
            miembro.guild.text_channels,
            name="bienvenidas"
        )

        if canal is None:
            return

        embed = discord.Embed(
            title="👋 ¡Nuevo miembro!",
            description=(
                f"¡Bienvenido/a {miembro.mention} "
                f"a **{miembro.guild.name}**!"
            )
        )

        embed.set_thumbnail(
            url=miembro.display_avatar.url
        )

        embed.add_field(
            name="👥 Miembros",
            value=miembro.guild.member_count
        )

        await canal.send(
            embed=embed
        )


    @commands.Cog.listener()
    async def on_member_remove(self, miembro):

        canal = discord.utils.get(
            miembro.guild.text_channels,
            name="bienvenidas"
        )

        if canal is None:
            return

        await canal.send(
            f"👋 **{miembro}** salió del servidor."
        )


async def setup(bot):
    await bot.add_cog(
        Bienvenida(bot)
    )