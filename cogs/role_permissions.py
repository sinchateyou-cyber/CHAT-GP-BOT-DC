import discord
from discord import app_commands
from discord.ext import commands

class RolePermissions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ============================================================
    # COMANDO: EDITAR PERMISOS DE UN ROL EN TODOS LOS CANALES
    # ============================================================
    @app_commands.command(
        name="permisos_rol",
        description="Modifica los permisos de un rol en TODOS los canales del servidor."
    )
    @app_commands.describe(
        rol="El rol al que le deseas modificar los permisos",
        leer_ver="Permite o bloquea ver los canales (True = Permitir, False = Denegar, None = Neutral)",
        enviar_mensajes="Permite o bloquea enviar mensajes en texto (True / False)",
        conectar_voz="Permite o bloquea conectarse a canales de voz (True / False)",
        hablar_voz="Permite o bloquea hablar en canales de voz (True / False)"
    )
    @app_commands.default_permissions(administrator=True)
    async def permisos_rol(
        self,
        interaction: discord.Interaction,
        rol: discord.Role,
        leer_ver: bool = None,
        enviar_mensajes: bool = None,
        conectar_voz: bool = None,
        hablar_voz: bool = None
    ):
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        if not guild:
            await interaction.followup.send("❌ Este comando solo se puede usar dentro de un servidor.", ephemeral=True)
            return

        # Verificar si el rol objetivo es superior o igual al rol más alto del bot
        if rol >= guild.me.top_role:
            await interaction.followup.send(
                f"❌ No puedo modificar permisos para el rol **{rol.name}** porque es igual o superior a mi rol más alto.",
                ephemeral=True
            )
            return

        # Definir los permisos según las opciones seleccionadas
        overwrite = discord.PermissionOverwrite()

        if leer_ver is not None:
            overwrite.view_channel = leer_ver
            overwrite.read_messages = leer_ver

        if enviar_mensajes is not None:
            overwrite.send_messages = enviar_mensajes

        if conectar_voz is not None:
            overwrite.connect = conectar_voz

        if hablar_voz is not None:
            overwrite.speak = hablar_voz

        canales_modificados = 0
        canales_fallidos = 0

        # Recorrer todos los canales (texto, voz, categorías, etc.)
        for channel in guild.channels:
            try:
                # Actualizar los permisos del rol en el canal (respeta los permisos previos no modificados)
                await channel.set_permissions(rol, overwrite=overwrite, reason=f"Permisos modificados por {interaction.user}")
                canales_modificados += 1
            except discord.Forbidden:
                canales_fallidos += 1
            except Exception:
                canales_fallidos += 1

        # Construir resumen del resultado
        mensaje = (
            f"✅ **Permisos actualizados para el rol {rol.mention}**\n\n"
            f"• **Canales modificados exitosamente:** `{canales_modificados}`\n"
        )
        if canales_fallidos > 0:
            mensaje += f"• ⚠️ **Canales sin permisos para modificar:** `{canales_fallidos}`\n"

        await interaction.followup.send(mensaje, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(RolePermissions(bot))
