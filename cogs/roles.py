import discord
from discord.ext import commands


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(
        self,
        ctx,
        miembro: discord.Member,
        *,
        rol: discord.Role
    ):

        if rol >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ Mi rol está por debajo de ese rol."
            )
            return

        await miembro.add_roles(rol)

        await ctx.send(
            f"✅ Se agregó {rol.mention} a "
            f"{miembro.mention}."
        )


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(
        self,
        ctx,
        miembro: discord.Member,
        *,
        rol: discord.Role
    ):

        await miembro.remove_roles(rol)

        await ctx.send(
            f"✅ Se quitó {rol.mention} de "
            f"{miembro.mention}."
        )


    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def autorole(
        self,
        ctx,
        *,
        rol: discord.Role
    ):

        config = self.bot.get_cog(
            "Roles"
        )

        await ctx.send(
            f"🎭 Para configurar autorole "
            f"usaremos el rol {rol.mention}."
        )


async def setup(bot):
    await bot.add_cog(
        Roles(bot)
    )