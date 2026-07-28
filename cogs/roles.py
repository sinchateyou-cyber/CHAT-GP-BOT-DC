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
    async def crearrol(self, ctx, *, nombre: str):
        # Comprobar si ya existe
        rol_existente = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if rol_existente:
            await ctx.send(
                f"❌ Ya existe un rol llamado **{nombre}**."
            )
            return
        # Crear rol
        rol = await ctx.guild.create_role(
            name=nombre,
            reason=f"Rol creado por {ctx.author}"
        )
        await ctx.send(
            f"✅ Rol creado correctamente: {rol.mention}"
        )
    # =========================
    # ELIMINAR ROL
    # =========================
    @commands.command(name="eliminarrol")
    @commands.has_permissions(manage_roles=True)
    async def eliminarrol(self, ctx, *, nombre: str):
        rol = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if not rol:
            await ctx.send(
                f"❌ No encontré ningún rol llamado **{nombre}**."
            )
            return
        # No permitir eliminar @everyone
        if rol.is_default():
            await ctx.send(
                "❌ No podés eliminar el rol @everyone."
            )
            return
        # Comprobar jerarquía
        if rol >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ No puedo eliminar ese rol porque está por encima "
                "o al mismo nivel que mi rol más alto."
            )
            return
        await rol.delete(
            reason=f"Rol eliminado por {ctx.author}"
        )
        await ctx.send(
            f"🗑️ El rol **{nombre}** fue eliminado correctamente."
        )
    # =========================
    # DAR ROL
    # =========================
    @commands.command(name="darrol")
    @commands.has_permissions(manage_roles=True)
    async def darrol(
        self,
        ctx,
        miembro: discord.Member,
        *,
        nombre: str
    ):
        rol = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if not rol:
            await ctx.send(
                f"❌ No encontré ningún rol llamado **{nombre}**."
            )
            return
        # Comprobar jerarquía
        if rol >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ No puedo asignar ese rol porque está por encima "
                "o al mismo nivel que mi rol más alto."
            )
            return
        if rol in miembro.roles:
            await ctx.send(
                f"❌ {miembro.mention} ya tiene el rol {rol.mention}."
            )
            return
        await miembro.add_roles(
            rol,
            reason=f"Rol asignado por {ctx.author}"
        )
        await ctx.send(
            f"✅ Se le dio el rol {rol.mention} a {miembro.mention}."
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
        nombre: str
    ):
        rol = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if not rol:
            await ctx.send(
                f"❌ No encontré ningún rol llamado **{nombre}**."
            )
            return
        # Comprobar jerarquía
        if rol >= ctx.guild.me.top_role:
            await ctx.send(
                "❌ No puedo quitar ese rol porque está por encima "
                "o al mismo nivel que mi rol más alto."
            )
            return
        if rol not in miembro.roles:
            await ctx.send(
                f"❌ {miembro.mention} no tiene el rol {rol.mention}."
            )
            return
        await miembro.remove_roles(
            rol,
            reason=f"Rol quitado por {ctx.author}"
        )
        await ctx.send(
            f"✅ Se quitó el rol {rol.mention} a {miembro.mention}."
        )
    # =========================
    # INFORMACIÓN DEL ROL
    # =========================
    @commands.command(name="rolinfo")
    async def rolinfo(self, ctx, *, nombre: str):
        rol = discord.utils.get(
            ctx.guild.roles,
            name=nombre
        )
        if not rol:
            await ctx.send(
                f"❌ No encontré ningún rol llamado **{nombre}**."
            )
            return
        embed = discord.Embed(
            title="📋 Información del rol",
            color=rol.color
        )
        embed.add_field(
            name="🏷️ Nombre",
            value=rol.name,
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=rol.id,
            inline=True
        )
        embed.add_field(
            name="👥 Miembros",
            value=len(rol.members),
            inline=True
        )
        embed.add_field(
            name="📌 Posición",
            value=rol.position,
            inline=True
        )
        embed.add_field(
            name="🔒 Mencionable",
            value="Sí" if rol.mentionable else "No",
            inline=True
        )
        embed.add_field(
            name="🤖 Administrado por bot",
            value="Sí" if rol.managed else "No",
            inline=True
        )
        await ctx.send(embed=embed)
    # =========================
    # ERRORES DE PERMISOS
    # =========================
    @crearrol.error
    @eliminarrol.error
    @darrol.error
    @quitarrol.error
    async def roles_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(
                "❌ Necesitás el permiso **Administrar roles** "
                "para usar este comando."
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                "❌ Faltan argumentos. Revisá cómo usar el comando."
            )
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(
                "❌ No encontré a ese miembro."
            )
        else:
            print(
                f"Error en comando de roles: {error}"
            )
async def setup(bot):
    await bot.add_cog(Roles(bot))