import discord
from discord import app_commands
from discord.ext import commands
class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    # ============================================================
    # /addrole
    # ============================================================
    @app_commands.command(
        name="addrole",
        description="Asigna un rol a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que quieres asignar el rol",
        rol="Rol que quieres asignar"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        rol: discord.Role
    ):
        # Comprobar jerarquía del bot
        if rol >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ No puedo asignar ese rol porque está por encima o al mismo nivel que mi rol más alto.",
                ephemeral=True
            )
        if rol in usuario.roles:
            return await interaction.response.send_message(
                f"⚠️ {usuario.mention} ya tiene el rol {rol.mention}.",
                ephemeral=True
            )
        try:
            await usuario.add_roles(rol)
            embed = discord.Embed(
                title="✅ Rol asignado",
                description=(
                    f"**Usuario:** {usuario.mention}\n"
                    f"**Rol:** {rol.mention}\n"
                    f"**Moderador:** {interaction.user.mention}"
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para asignar ese rol.",
                ephemeral=True
            )
    # ============================================================
    # /removerole
    # ============================================================
    @app_commands.command(
        name="removerole",
        description="Quita un rol a un usuario."
    )
    @app_commands.describe(
        usuario="Usuario al que quieres quitarle el rol",
        rol="Rol que quieres quitar"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removerole(
        self,
        interaction: discord.Interaction,
        usuario: discord.Member,
        rol: discord.Role
    ):
        if rol >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ No puedo quitar ese rol porque está por encima o al mismo nivel que mi rol más alto.",
                ephemeral=True
            )
        if rol not in usuario.roles:
            return await interaction.response.send_message(
                f"⚠️ {usuario.mention} no tiene el rol {rol.mention}.",
                ephemeral=True
            )
        try:
            await usuario.remove_roles(rol)
            embed = discord.Embed(
                title="✅ Rol eliminado",
                description=(
                    f"**Usuario:** {usuario.mention}\n"
                    f"**Rol:** {rol.mention}\n"
                    f"**Moderador:** {interaction.user.mention}"
                ),
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos suficientes para quitar ese rol.",
                ephemeral=True
            )
    # ============================================================
    # /createrole
    # ============================================================
    @app_commands.command(
        name="createrole",
        description="Crea un nuevo rol en el servidor."
    )
    @app_commands.describe(
        nombre="Nombre del nuevo rol"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def createrole(
        self,
        interaction: discord.Interaction,
        nombre: str
    ):
        try:
            rol = await interaction.guild.create_role(
                name=nombre,
                reason=f"Creado por {interaction.user}"
            )
            embed = discord.Embed(
                title="✅ Rol creado",
                description=(
                    f"El rol {rol.mention} fue creado correctamente."
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para crear roles.",
                ephemeral=True
            )
    # ============================================================
    # /deleterole
    # ============================================================
    @app_commands.command(
        name="deleterole",
        description="Elimina un rol del servidor."
    )
    @app_commands.describe(
        rol="Rol que quieres eliminar"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    async def deleterole(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):
        if rol >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                "❌ No puedo eliminar ese rol porque está por encima o al mismo nivel que mi rol más alto.",
                ephemeral=True
            )
        try:
            nombre_rol = rol.name
            await rol.delete(
                reason=f"Eliminado por {interaction.user}"
            )
            embed = discord.Embed(
                title="🗑️ Rol eliminado",
                description=(
                    f"El rol **{nombre_rol}** fue eliminado correctamente."
                ),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No tengo permisos para eliminar ese rol.",
                ephemeral=True
            )
    # ============================================================
    # /roleinfo
    # ============================================================
    @app_commands.command(
        name="roleinfo",
        description="Muestra información sobre un rol."
    )
    @app_commands.describe(
        rol="Rol del que quieres obtener información"
    )
    async def roleinfo(
        self,
        interaction: discord.Interaction,
        rol: discord.Role
    ):
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
            value=str(rol.id),
            inline=True
        )
        embed.add_field(
            name="👥 Miembros",
            value=str(len(rol.members)),
            inline=True
        )
        embed.add_field(
            name="📌 Posición",
            value=str(rol.position),
            inline=True
        )
        embed.add_field(
            name="🔒 Mencionable",
            value="Sí" if rol.mentionable else "No",
            inline=True
        )
        embed.add_field(
            name="🤖 Gestionado",
            value="Sí" if rol.managed else "No",
            inline=True
        )
        await interaction.response.send_message(embed=embed)
# ============================================================
# MANEJO DE ERRORES
# ============================================================
    @addrole.error
    async def addrole_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso **Gestionar roles** para usar este comando.",
                ephemeral=True
            )
    @removerole.error
    async def removerole_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso **Gestionar roles** para usar este comando.",
                ephemeral=True
            )
    @createrole.error
    async def createrole_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso **Gestionar roles** para usar este comando.",
                ephemeral=True
            )
    @deleterole.error
    async def deleterole_error(
        self,
        interaction: discord.Interaction,
        error
    ):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "❌ Necesitas el permiso **Gestionar roles** para usar este comando.",
                ephemeral=True
            )
async def setup(bot):
    await bot.add_cog(Roles(bot))

📁 Ubicación

Guardalo en:

cogs/roles.py

⚙️ Comandos disponibles

* /addrole usuario rol
* /removerole usuario rol
* /createrole nombre
* /deleterole rol
* /roleinfo rol

El bot necesita tener el permiso Gestionar roles y su rol debe estar por encima de los roles que quiere administrar.