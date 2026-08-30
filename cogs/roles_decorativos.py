import discord
from discord.ext import commands

class RolesDecorativos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def decorativo(self, ctx):
        """Comando base para la gestión de roles decorativos."""
        await ctx.send("Usa `!decorativo crear <nombre>` o `!decorativo asignar <rol>`.")

    @decorativo.command(name="crear")
    @commands.has_permissions(manage_roles=True)
    async def crear_rol(self, ctx, nombre: str, color_hex: str = "000000"):
        """Crea un rol decorativo sin permisos especiales."""
        try:
            color = discord.Color(int(color_hex.lstrip("#"), 16))
            rol = await ctx.guild.create_role(
                name=nombre,
                color=color,
                permissions=discord.Permissions.none(),  # Sin permisos
                reason="Rol decorativo creado por comando"
            )
            await ctx.send(f"Rol decorativo **{rol.name}** creado con éxito.")
        except ValueError:
            await ctx.send("El código de color Hex no es válido. Usa formato como `FF5733`.")

    @decorativo.command(name="asignar")
    async def asignar_rol(self, ctx, rol: discord.Role):
        """Asigna un rol decorativo al usuario que lo solicita."""
        if rol in ctx.author.roles:
            await ctx.author.remove_roles(rol)
            await ctx.send(f"Se te ha quitado el rol **{rol.name}**.")
        else:
            await ctx.author.add_roles(rol)
            await ctx.send(f"Se te ha asignado el rol **{rol.name}**.")

async def setup(bot):
    await bot.add_cog(RolesDecorativos(bot))
