import discord
from discord.ext import commands
class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # =========================
    # CREAR ROL
    # =========================
    @commands.command(name="crearrol")
    @commands.has_permissions(manage_roles=True)
    async def crearrol(self, ctx, *, nombre):
        try:
            rol = await ctx.guild.create_role(
                name=nombre,
                reason=f"Creado por {ctx.author}"
            )
            await ctx.send(
                f"✅ Rol creado correctamente: {rol.mention}"
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ No tengo permisos para crear roles."
            )
        except Exception as error:
            print(f"Error creando rol: {error}")
            await ctx.send(
                "❌ Ocurrió un error al crear el rol."
            )
    # =========================
    # ELIMINAR ROL
    # =========================
    @commands.command(name="eliminarrol")
    @commands.has_permissions(manage_roles=True)
    async def eliminarrol(self, ctx, *, nombre):
        rol = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if rol is None:
            await ctx.send(
                f"❌ No existe un rol llamado **{nombre}**."
            )
            return
        if rol.is_default():
            await ctx.send(
                "❌ No podés eliminar el rol @everyone."
            )
            return
        try:
            await rol.delete(
                reason=f"Eliminado por {ctx.author}"
            )
            await ctx.send(
                f"🗑️ El rol **{nombre}** fue eliminado."
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ No puedo eliminar ese rol. "
                "Asegurate de que mi rol esté por encima."
            )
    # =========================
    # DAR ROL
    # =========================
    @commands.command(name="darrol")
    @commands.has_permissions(manage_roles=True)
    async def darrol(self, ctx, miembro: discord.Member, *, nombre):
        rol = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if rol is None:
            await ctx.send(
                f"❌ No existe un rol llamado **{nombre}**."
            )
            return
        if rol >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ Mi rol está por debajo de ese rol."
            )
            return
        try:
            await miembro.add_roles(rol)
            await ctx.send(
                f"✅ {rol.mention} fue dado a {miembro.mention}."
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ No tengo permisos para dar ese rol."
            )
    # =========================
    # QUITAR ROL
    # =========================
    @commands.command(name="quitarrol")
    @commands.has_permissions(manage_roles=True)
    async def quitarrol(
        self,
        ctx,
        miembro: discord.Member,
        *,
        nombre
    ):
        rol = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if rol is None:
            await ctx.send(
                f"❌ No existe un rol llamado **{nombre}**."
            )
            return
        try:
            await miembro.remove_roles(rol)
            await ctx.send(
                f"✅ {rol.mention} fue quitado de {miembro.mention}."
            )
        except discord.Forbidden:
            await ctx.send(
                "❌ No tengo permisos para quitar ese rol."
            )
async def setup(bot):
    await bot.add_cog(Roles(bot))