import discord
from discord.ext import commands


class Bienvenida(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =========================
    # NUEVO MIEMBRO
    # =========================

    @commands.Cog.listener()
    async def on_member_join(self, miembro):

        canal = discord.utils.get(
            miembro.guild.text_channels,
            name="bienvenidas"
        )

        if canal is None:
            return

        embed = discord.Embed(
            title="👋 ¡Bienvenido/a!",
            description=(
                f"¡Hola {miembro.mention}!\n\n"
                f"Bienvenido/a a **{miembro.guild.name}** 🎉"
            )
        )

        embed.set_thumbnail(
            url=miembro.display_avatar.url
        )

        embed.add_field(
            name="👥 Miembros",
            value=str(
                miembro.guild.member_count
            ),
            inline=True
        )

        embed.set_footer(
            text="¡Esperamos que la pases genial!"
        )

        await canal.send(
            embed=embed
        )

    # =========================
    # MIEMBRO SE VA
    # =========================

    @commands.Cog.listener()
    async def on_member_remove(self, miembro):

        canal = discord.utils.get(
            miembro.guild.text_channels,
            name="bienvenidas"
        )

        if canal is None:
            return

        embed = discord.Embed(
            title="👋 Miembro salió",
            description=(
                f"**{miembro}** abandonó "
                f"el servidor."
            )
        )

        embed.set_thumbnail(
            url=miembro.display_avatar.url
        )

        await canal.send(
            embed=embed
        )


async def setup(bot):
    await bot.add_cog(
        Bienvenida(bot)
    )